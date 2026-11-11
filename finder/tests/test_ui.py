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
    app.run()  # Dashboard reads the inventory before offering search.
    assert app.error and not app.exception
    assert path.read_text()=='broken'


def test_ui_star_sticker_interpretation_and_score(tmp_path, monkeypatch):
    import json
    app, path = setup_app(tmp_path, monkeypatch)
    path.write_text(json.dumps([dict(id=501, category='bottle', color='blue',
        brand='milton', location='library', mark='star', status='available')]))
    app.text_input(key='query').input('blue Milton bottle canteen star sticker').run()
    app.button(key='search').click().run()
    assert not app.exception and not app.warning
    assert any('Item #501' in s.value for s in app.subheader)
    assert any('90.00' in m.value for m in app.markdown)
    app.text_input(key='query').input('bottle not star sticker').run()
    app.button(key='search').click().run()
    assert any('No matching' in i.value for i in app.info)


def test_ui_legacy_runtime_remains_searchable(tmp_path, monkeypatch):
    import json
    app, path = setup_app(tmp_path, monkeypatch)
    original = json.dumps([dict(id=501, category='backpack', color='black',
        brand='none', location='library', mark='none', status='available')])
    path.write_text(original)
    app.text_input(key='query').input('black bag library').run()
    app.button(key='search').click().run()
    assert not app.exception and not app.error
    assert any('Item #501' in s.value for s in app.subheader)
    assert path.read_text() == original


def test_dashboard_inventory_totals_and_return_refresh(tmp_path, monkeypatch):
    import json
    app, path = setup_app(tmp_path, monkeypatch)
    path.write_text(json.dumps([
        dict(id=1, category='bottle', color='blue', brand='milton', location='library', mark='star', status='available'),
        dict(id=2, category='keys', color='black', brand=None, location='canteen', mark=None, status='returned')]))
    app.run()
    assert {m.label: m.value for m in app.metric} == {'Recorded':'2','Available':'1','Returned':'1','Locations':'2'}
    app.switch_page('views/staff.py').run()
    assert not app.exception
    app.checkbox(key='confirmed').check()
    app.button[0].click().run()
    assert not app.exception and app.success
    assert {m.label: m.value for m in app.metric}['Returned'] == '2'
    assert {m.label: m.value for m in app.metric}['Available'] == '0'
    assert not app.button


def test_all_dashboard_pages_handle_empty_inventory(tmp_path, monkeypatch):
    app, _ = setup_app(tmp_path, monkeypatch)
    for page in ['views/search.py','views/report.py','views/staff.py']:
        app.switch_page(page).run()
        assert not app.exception
        assert app.info


def test_results_clear_when_query_changes(tmp_path, monkeypatch):
    from finder_core.storage import add_item
    app, path = setup_app(tmp_path, monkeypatch)
    add_item(dict(category='bottle',color='blue',brand='milton',location='library',mark='star'),path)
    app.text_input(key='query').input('blue bottle').run()
    app.button(key='search').click().run()
    assert any('Item #' in s.value for s in app.subheader)
    app.text_input(key='query').input('keys').run()
    assert not any('Item #' in s.value for s in app.subheader)


def test_ui_did_you_mean_button_fixes_the_query(tmp_path,monkeypatch):
    app,_=setup_app(tmp_path,monkeypatch)
    app.switch_page('views/search.py').run()
    app.text_input(key='query').input('Miltn bottles').run()
    assert any('Did you mean **Milton**' in m.value for m in app.markdown)
    app.button(key='fix_miltn').click().run()
    assert app.text_input(key='query').value=='milton bottles'
    assert not any('Did you mean' in m.value for m in app.markdown)
    assert not app.exception
