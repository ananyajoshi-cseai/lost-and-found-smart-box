from pathlib import Path
from streamlit.testing.v1 import AppTest
from finder_core.storage import load_items

ENTRY=Path(__file__).resolve().parents[1]/'streamlit_app.py'


def setup_app(tmp_path,monkeypatch):
    path=tmp_path/'items.json'
    path.write_text('[]')
    monkeypatch.setenv('FINDER_DATA_PATH',str(path))
    return AppTest.from_file(str(ENTRY),default_timeout=45).run(),path


def test_ui_report_search_return(tmp_path,monkeypatch):
    app,path=setup_app(tmp_path,monkeypatch)
    assert not app.exception
    app.switch_page('views/report.py').run()
    app.selectbox(key='brand').select('milton')
    app.button[0].click().run()
    assert app.success and not app.exception
    item=load_items(path)[0]
    app.switch_page('views/search.py').run()
    app.text_input(key='query').input('navy Milton flask').run()
    app.button(key='search').click().run()
    assert any('Item #' in s.value for s in app.subheader)
    assert len(app.table)==1 and not app.exception
    app.switch_page('views/staff.py').run()
    app.button[0].click().run()
    assert app.error and load_items(path)[0]['status']=='available'
    app.checkbox(key='confirmed').check()
    app.button[0].click().run()
    assert app.success and load_items(path)[0]['status']=='returned'
    app.switch_page('views/search.py').run()
    app.text_input(key='query').input('navy Milton flask').run()
    app.button(key='search').click().run()
    assert any('No matching' in i.value for i in app.info)
    assert not app.exception


def test_ui_clarification_and_empty(tmp_path,monkeypatch):
    app,_=setup_app(tmp_path,monkeypatch)
    app.text_input(key='query').input('red blue bottle').run()
    app.button(key='search').click().run()
    assert any('clarify' in w.value for w in app.warning)
    app.text_input(key='query').input('something lost').run()
    app.button(key='search').click().run()
    assert any('known category' in i.value for i in app.info)
    assert not app.exception


def test_ui_corrupt_file_visible(tmp_path,monkeypatch):
    app,path=setup_app(tmp_path,monkeypatch)
    path.write_text('broken')
    app.text_input(key='query').input('bottle').run()
    app.button(key='search').click().run()
    assert app.error and not app.exception
    assert path.read_text()=='broken'
