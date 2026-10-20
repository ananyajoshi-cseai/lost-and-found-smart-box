import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from finder_core import storage
from finder_core.engine import parse, rank

ITEM = dict(category='bottle',color='blue',brand='milton',location='library',mark='star')


def test_report_search_return_restart(tmp_path):
    path=tmp_path/'items.json'
    path.write_text('[]')
    item=storage.add_item(ITEM,path)
    assert rank(parse('navy Milton flask'),storage.load_items(path))[0]['id']==item['id']
    storage.mark_returned(item['id'],path)
    assert storage.load_items(path)[0]['status']=='returned'
    assert rank(parse('navy Milton flask'),storage.load_items(path))==[]
    with pytest.raises(ValueError): storage.mark_returned(item['id'],path)
    with pytest.raises(ValueError): storage.mark_returned(999,path)


def test_seed_only_when_missing(tmp_path):
    path=tmp_path/'items.json'
    assert len(storage.load_items(path))==40
    path.write_text('[]')
    assert storage.load_items(path)==[]


@pytest.mark.parametrize('content',['broken','{}','[{"id":1}]'])
def test_corrupt_data_never_reset(tmp_path,content):
    path=tmp_path/'items.json'
    path.write_text(content)
    with pytest.raises(ValueError): storage.load_items(path)
    with pytest.raises(ValueError): storage.add_item(ITEM,path)
    assert path.read_text()==content


def test_atomic_write_failure_preserves_original(tmp_path,monkeypatch):
    path=tmp_path/'items.json'
    path.write_text('[]')
    def fail(*args): raise OSError('simulated disk failure')
    monkeypatch.setattr(storage.os,'replace',fail)
    with pytest.raises(OSError): storage.add_item(ITEM,path)
    assert path.read_text()=='[]'
    assert not list(tmp_path.glob('*.tmp'))


def test_concurrent_adds_have_unique_ids(tmp_path):
    path=tmp_path/'items.json'
    path.write_text('[]')
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:storage.add_item(ITEM,path),range(8)))
    assert len({i['id'] for i in results})==8
    assert len(storage.load_items(path))==8


@pytest.mark.parametrize('change',[{'category':'flask'},{'color':None},{'brand':'unknown'},{'extra':'field'}])
def test_invalid_fields_rejected_before_write(tmp_path,change):
    path=tmp_path/'items.json'
    with pytest.raises(ValueError): storage.add_item({**ITEM,**change},path)
    assert not path.exists()


def test_duplicate_ids_rejected(tmp_path):
    path=tmp_path/'items.json'
    row={**ITEM,'id':1,'status':'available'}
    path.write_text(json.dumps([row,row]))
    with pytest.raises(ValueError): storage.load_items(path)

def test_invalid_status_type_is_read_error(tmp_path):
    path=tmp_path/'items.json'
    path.write_text(json.dumps([{**ITEM,'id':1,'status':[]}]))
    with pytest.raises(ValueError): storage.load_items(path)
