"""Regression checks at the knowledge/reasoning/storage integration boundaries."""
import json

import pytest

from finder_core.engine import parse, rank
from finder_core.ontology import GRAPH, bfs, get_related_categories
from finder_core.storage import SEED, load_items, add_item, mark_returned, validate_items
from finder_core.vocabulary import VOCAB


@pytest.mark.parametrize('prefix', ['', 'not ', 'no ', 'without '])
def test_longest_mark_phrase_with_negation(prefix):
    query = parse('bottle ' + prefix + 'star sticker')
    assert query['ambiguous'] == []
    if prefix:
        assert query['positive'] == {'category': 'bottle'}
        assert query['excluded'] == {'mark': ['star']}
    else:
        assert query['positive'] == {'category': 'bottle', 'mark': 'star'}
        assert query['excluded'] == {}
    assert parse('bottle sticker')['positive']['mark'] == 'sticker'


def test_proposal_worked_example_and_exclusion():
    item = dict(id=101, category='bottle', color='blue', brand='milton',
                location='library', mark='star', status='available')
    result = rank(parse('blue Milton bottle canteen star sticker'), [item])[0]
    assert result['score'] == 90
    assert result['reasons'] == {'category': 40, 'color': 25, 'brand': 15,
                                 'location': 0, 'mark': 10}
    assert result['strong_candidate'] and result['coverage'] == 5
    assert rank(parse('bottle not star sticker'), [item]) == []
    assert parse('bottle star sticker stripe')['ambiguous'] == ['mark']


def test_every_alias_has_one_canonical_interpretation():
    for field, values in VOCAB.items():
        for canonical, aliases in values.items():
            assert canonical in aliases
            for alias in aliases:
                query = parse(alias)
                assert query == {'positive': {field: canonical}, 'excluded': {},
                                 'ambiguous': []}, (field, alias, query)


def test_all_supported_categories_are_reachable_with_bounded_distances():
    assert set(VOCAB['category']) <= set(GRAPH)
    for category in VOCAB['category']:
        distances = bfs(category)
        assert distances[category] == 0
        assert all(0 <= distance <= 2 for distance in distances.values())
        assert set(bfs(category, 0)) == {category}
        for node, distance in distances.items():
            if distance:
                assert any(distances.get(parent) == distance - 1 for parent in GRAPH[node])
        assert category not in get_related_categories(category)
    assert get_related_categories('unknown') == []
    assert bfs('backpack')['bottle'] == 2
    assert bfs('glasses')['wallet'] == 2
    assert 'wallet' not in bfs('backpack')


@pytest.mark.parametrize('depth', [-1, 1.5, True, '2'])
def test_invalid_bfs_depth_is_rejected(depth):
    with pytest.raises(ValueError):
        bfs('bottle', depth)


@pytest.mark.parametrize('category,sibling', [('backpack', 'bottle'), ('glasses', 'wallet')])
def test_new_categories_use_explicit_related_fallback(category, sibling):
    item = dict(id=1, category=sibling, color='black', brand='nike',
                location='library', mark='logo', status='available')
    query = parse(f'{category} black nike library logo')
    assert rank(query, [item]) == []
    result = rank(query, [item], broaden=True)[0]
    assert result['score'] == 60 and result['related']
    assert result['reasons']['category'] == 0 and not result['strong_candidate']


def test_every_seed_record_can_be_parsed_scored_and_round_tripped(tmp_path):
    items = json.loads(SEED.read_text(encoding='utf-8-sig'))
    validate_items(items)
    assert len(items) == 40
    assert set(row['category'] for row in items) == set(VOCAB['category'])
    path = tmp_path / 'items.json'
    path.write_text('[]')
    for original in items:
        facts = {field: original[field] for field in VOCAB}
        query = parse(' '.join(value for value in facts.values() if value is not None))
        assert query['ambiguous'] == []
        assert query['positive'] == {k: v for k, v in facts.items() if v is not None}
        saved = add_item(facts, path)
        result = rank(query, [saved])[0]
        assert result['score'] == 100
        assert result['coverage'] == len(query['positive'])
        mark_returned(saved['id'], path)
    assert len(load_items(path)) == 40
    assert all(item['status'] == 'returned' for item in load_items(path))
    assert rank(parse('bottle'), load_items(path)) == []


@pytest.mark.parametrize('legacy', ['none', '', ' None '])
def test_legacy_optional_values_read_without_rewriting_and_survive_update(tmp_path, legacy):
    row = dict(id=71, category='bottle', color='blue', brand=legacy,
               location='library', mark=legacy, status='available')
    path = tmp_path / 'items.json'
    original = json.dumps([row])
    path.write_text(original)
    loaded = load_items(path)
    assert loaded == [{**row, 'brand': None, 'mark': None}]
    assert path.read_text() == original
    assert rank(parse('blue bottle'), loaded)[0]['id'] == 71
    mark_returned(71, path)
    assert load_items(path) == [{**row, 'brand': None, 'mark': None, 'status': 'returned'}]
    assert json.loads(path.read_text())[0]['mark'] is None


def test_legacy_conversion_does_not_hide_invalid_records(tmp_path):
    path = tmp_path / 'items.json'
    original = json.dumps([dict(id=71, category='flask', color='blue', brand='none',
                               location='library', mark='none', status='available')])
    path.write_text(original)
    with pytest.raises(ValueError):
        load_items(path)
    assert path.read_text() == original


def test_failed_update_does_not_rewrite_legacy_data(tmp_path, monkeypatch):
    from finder_core import storage
    row = dict(id=71, category='bottle', color='blue', brand='none',
               location='library', mark='none', status='available')
    path = tmp_path / 'items.json'
    original = json.dumps([row])
    path.write_text(original)
    def fail(*args):
        raise OSError('simulated disk failure')
    monkeypatch.setattr(storage.os, 'replace', fail)
    with pytest.raises(OSError):
        mark_returned(71, path)
    assert path.read_text() == original
