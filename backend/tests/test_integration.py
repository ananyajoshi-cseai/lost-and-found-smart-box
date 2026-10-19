"""Real loopback HTTP + the committed replay script; no simulated hardware claim."""
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

import httpx
from PIL import Image
import uvicorn
from app.main import app
from app.recovery import backup, restore

AUTH=('integration-staff','integration-password')


@contextmanager
def running_server():
    sock=socket.socket()
    sock.bind(('127.0.0.1',0))
    port=sock.getsockname()[1]
    server=uvicorn.Server(uvicorn.Config(app,log_level='error'))
    thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True)
    thread.start()
    try:
        deadline=time.monotonic()+10
        while not server.started:
            if not thread.is_alive() or time.monotonic()>deadline:
                raise RuntimeError('Test server did not start')
            time.sleep(0.01)
        with httpx.Client(base_url=f'http://127.0.0.1:{port}',timeout=5) as client:
            yield client
    finally:
        server.should_exit=True
        thread.join(timeout=10)
        sock.close()
        if thread.is_alive(): raise RuntimeError('Test server did not stop')


def test_real_replay_to_return_and_restored_restart(tmp_path,monkeypatch):
    database=tmp_path/'original.db'
    uploads=tmp_path/'original-uploads'
    for key,value in {'DATABASE_PATH':str(database),'UPLOAD_DIR':str(uploads),'DEVICE_KEY':'integration-device',
                      'STAFF_USERNAME':AUTH[0],'STAFF_PASSWORD':AUTH[1]}.items():
        monkeypatch.setenv(key,value)
    event={'event_id':'integration-event','device_id':'box01','kind':'deposit'}
    event_file=tmp_path/'event.json'
    event_file.write_text(json.dumps(event))
    replay=Path(__file__).resolve().parents[2]/'hardware/simulation/replay.py'
    photo=io.BytesIO()
    Image.new('RGB',(20,20),'blue').save(photo,'PNG')
    with running_server() as client:
        env={**os.environ,'API_URL':str(client.base_url).rstrip('/')}
        for expected in ['201','200']:
            run=subprocess.run([sys.executable,str(replay),str(event_file)],env=env,capture_output=True,text=True,timeout=10)
            assert run.returncode==0 and run.stdout.startswith(expected)
        bad_env={**env,'DEVICE_KEY':'incorrect'}
        denied=subprocess.run([sys.executable,str(replay),str(event_file)],env=bad_env,capture_output=True,text=True,timeout=10)
        assert denied.returncode==1 and 'HTTP 401' in denied.stderr and not denied.stdout
        conflicting=tmp_path/'conflict.json'
        conflicting.write_text(json.dumps({**event,'device_id':'different-box'}))
        conflict=subprocess.run([sys.executable,str(replay),str(conflicting)],env=env,capture_output=True,text=True,timeout=10)
        assert conflict.returncode==1 and 'HTTP 409' in conflict.stderr
        assert len(client.get('/api/admin/events',auth=AUTH).json()['events'])==1
        ids=[]
        for index in range(2):
            if index:
                event={**event,'event_id':'integration-second'}
                assert client.post('/api/device/events',headers={'X-Device-Key':env['DEVICE_KEY']},json=event).status_code==201
            registration=client.post('/api/items',auth=AUTH,data={'event_id':event['event_id'],'category':'bottle','color':'blue',
                'brand':'milton','location':'library','mark':'star','private_mark':'synthetic hidden detail'},
                files={'photo':('sample.png',photo.getvalue(),'image/png')})
            assert registration.status_code==201
            ids.append(registration.json()['id'])
        assert ids[0] in [r['id'] for r in client.post('/api/search',json={'query':'navy Milton flask'}).json()['results']]
        claims=[]
        for i in range(2):
            response=client.post('/api/claims',json={'item_id':ids[0],'contact':f'demo{i}@example.invalid','evidence':'synthetic detail'})
            assert response.status_code==201
            claims.append(response.json()['claim_id'])
        url=f'/api/admin/claims/{claims[0]}/approve'
        assert client.post(url,json={'reason':'synthetic comparison'}).status_code==401
        assert client.post(url,auth=AUTH,json={'reason':'synthetic comparison'}).status_code==200
        assert client.post(f'/api/admin/claims/{claims[1]}/approve',auth=AUTH,json={'reason':'second comparison'}).status_code==409
        assert client.get(f'/api/items/{ids[0]}/photo').status_code==404
        available_photo=client.get(f'/api/items/{ids[1]}/photo').content
        before=client.get('/api/admin/claims',auth=AUTH).json()
    # Failed network delivery is visible and does not rewrite the saved event.
    failed=subprocess.run([sys.executable,str(replay),str(event_file)],env=env,capture_output=True,text=True,timeout=10)
    assert failed.returncode==1 and 'Replay failed' in failed.stderr and not failed.stdout
    assert json.loads(event_file.read_text())['event_id']=='integration-event'
    # The server is fully stopped: back up database AND referenced images.
    bundle=tmp_path/'backup'
    backup(database,uploads,bundle,server_stopped=True)
    restored=restore(bundle,tmp_path/'restored')
    monkeypatch.setenv('DATABASE_PATH',str(restored/'smartbox.db'))
    monkeypatch.setenv('UPLOAD_DIR',str(restored/'uploads'))
    with running_server() as client:
        assert client.get('/api/admin/claims',auth=AUTH).json()==before
        assert client.get(f'/api/items/{ids[0]}').status_code==404
        assert client.get(f'/api/items/{ids[1]}/photo').content==available_photo
        results=client.post('/api/search',json={'query':'navy Milton flask'}).json()['results']
        assert [r['id'] for r in results]==[ids[1]]
        assert client.get('/health').json()=={'status':'ok'}
    assert database.exists() and uploads.is_dir()
