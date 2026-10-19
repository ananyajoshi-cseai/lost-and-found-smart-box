import json
from pathlib import Path
import sqlite3
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from app.database import initialize, connect
from app.recovery import backup, restore, verify, digest
from app.ui import configure_ui


@pytest.fixture
def source(tmp_path, monkeypatch):
    database = tmp_path / "source.db"
    uploads = tmp_path / "photos"
    uploads.mkdir()
    name = "a"*32 + ".jpg"
    Image.new("RGB",(8,8),"blue").save(uploads/name)
    monkeypatch.setenv("DATABASE_PATH",str(database))
    initialize()
    with connect() as db:
        db.execute("INSERT INTO device_events(event_id,device_id,kind) VALUES('event','box01','deposit')")
        db.execute("INSERT INTO items(event_id,category,color,location,photo_path) VALUES('event','bottle','blue','library',?)",(name,))
        db.execute("INSERT INTO claim_requests(item_id,contact,evidence) VALUES(1,'synthetic@example.invalid','private')")
    return database, uploads


def test_backup_restore_is_verified_and_never_overwrites(source,tmp_path):
    database,uploads=source
    original=digest(database)
    bundle=tmp_path/'backup'
    result=backup(database,uploads,bundle,server_stopped=True)
    assert result['row_counts']['claim_requests']==1
    assert verify(bundle)==result
    destination=restore(bundle,tmp_path/'restored')
    assert (destination/'RESTORE_COMPLETE.json').is_file()
    assert digest(database)==original and digest(destination/'smartbox.db')==digest(bundle/'smartbox.db')
    with pytest.raises(FileExistsError): restore(bundle,destination)
    with pytest.raises(FileExistsError): backup(database,uploads,bundle,server_stopped=True)
    with pytest.raises(ValueError): backup(database,uploads,tmp_path/'not-stopped')
    assert not (tmp_path/'not-stopped').exists()


@pytest.mark.parametrize('kind',['database','photo','missing','path','counts','null'])
def test_corrupt_or_malicious_bundle_rejected_before_restore(source,tmp_path,kind):
    database,uploads=source
    bundle=tmp_path/'backup'
    backup(database,uploads,bundle,server_stopped=True)
    manifest=json.loads((bundle/'manifest.json').read_text())
    if kind=='database': (bundle/'smartbox.db').write_bytes(b'broken')
    elif kind=='photo': next((bundle/'uploads').glob('*.jpg')).write_bytes(b'broken')
    elif kind=='missing': next((bundle/'uploads').glob('*.jpg')).unlink()
    elif kind=='path': manifest['files']['../outside.txt']='0'*64
    elif kind=='counts': manifest['row_counts']['items']=999
    elif kind=='null': manifest=None
    (bundle/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError): restore(bundle,tmp_path/'restore')
    assert not (tmp_path/'restore').exists()


def test_failed_backup_has_no_completion_manifest(source,tmp_path):
    database,uploads=source
    next(uploads.glob('*.jpg')).unlink()
    with pytest.raises(ValueError): backup(database,uploads,tmp_path/'bad',server_stopped=True)
    assert not (tmp_path/'bad'/'manifest.json').exists()
    with pytest.raises(ValueError): verify(tmp_path/'bad')
    with pytest.raises(ValueError): backup(tmp_path/'absent.db',uploads,tmp_path/'new',server_stopped=True)
    assert not (tmp_path/'absent.db').exists()


def test_database_integrity_and_references_checked(source,tmp_path):
    database,uploads=source
    with sqlite3.connect(database) as db:
        db.execute("INSERT INTO claim_requests(item_id,contact,evidence) VALUES(999,'x','x')")
    with pytest.raises(ValueError,match='foreign keys'):
        backup(database,uploads,tmp_path/'bad',server_stopped=True)


def test_ui_missing_then_real_assets_same_origin(tmp_path,monkeypatch):
    monkeypatch.delenv('CORS_ORIGINS',raising=False)
    frontend=tmp_path/'frontend'
    frontend.mkdir()
    application=FastAPI()
    configure_ui(application,frontend)
    with TestClient(application) as client:
        assert client.get('/ui',follow_redirects=False).status_code==307
        assert client.get('/ui/').status_code==503
        (frontend/'index.html').write_text('<h1>Frontend test fixture, not the team UI</h1>')
        (frontend/'test.js').write_text('fetch("/health")')
        assert 'Frontend test fixture' in client.get('/ui/').text
        assert client.get('/ui/test.js').status_code==200
        (tmp_path/'private.txt').write_text('SECRET')
        assert client.get('/ui/%2e%2e/private.txt').status_code==404
        assert client.get('/ui/uploads/private.jpg').status_code==404
        assert 'access-control-allow-origin' not in client.get('/ui/').headers


def test_cors_only_explicit_development_origins(tmp_path,monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS','http://localhost:5500,http://127.0.0.1:5500')
    app=FastAPI()
    configure_ui(app,tmp_path)
    with TestClient(app) as client:
        headers={'Origin':'http://localhost:5500','Access-Control-Request-Method':'POST',
                 'Access-Control-Request-Headers':'authorization,content-type'}
        response=client.options('/api/items',headers=headers)
        assert response.status_code==200
        assert response.headers['access-control-allow-origin']=='http://localhost:5500'
        assert client.options('/api/items',headers={**headers,'Origin':'https://unknown.invalid'}).status_code==400
    monkeypatch.setenv('CORS_ORIGINS','*')
    with pytest.raises(ValueError): configure_ui(FastAPI(),tmp_path)
