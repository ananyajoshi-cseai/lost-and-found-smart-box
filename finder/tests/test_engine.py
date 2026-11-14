import pytest
from finder_core.engine import parse, bfs, rank

ITEM = dict(id=101, category="bottle", color="blue", brand="milton", location="library", mark="star", status="available")

@pytest.mark.parametrize("text,expected", [
 ("navy flask", {"category":"bottle","color":"blue"}),
 ("I misplaced my dark blue Milton water bottle near the library.", {"category":"bottle","color":"blue","brand":"milton","location":"library"}),
 ("Miltn bottle", {"category":"bottle"}),
 ("something lost", {})])
def test_parse(text, expected):
 assert parse(text)["positive"] == expected

@pytest.mark.parametrize("text", ["bottle not blue", "not dark blue bottle", "bottle without navy", "bottle no blue"])
def test_negation(text):
 q=parse(text)
 assert q["excluded"] == {"color":["blue"]}
 assert rank(q,[ITEM]) == []

@pytest.mark.parametrize("text", ["red blue bottle", "blue not blue bottle"])
def test_ambiguity(text):
 q=parse(text)
 assert "color" in q["ambiguous"]
 assert rank(q,[ITEM]) == []

def test_score_arithmetic_and_strong_rule():
 r=rank(parse("blue milton bottle canteen star"),[ITEM])[0]
 assert r["score"] == 90
 assert r["coverage"] == 5 and r["strong_candidate"]
 assert sum(r["reasons"].values()) == 90
 assert rank(parse("blue milton bottle canteen"),[ITEM])[0]["score"] == 88.89

def test_omitted_fields_and_missing_values():
 assert rank(parse("bottle"),[ITEM])[0]["score"] == 100
 assert rank(parse("bottle"),[ITEM])[0]["coverage"] == 1
 assert rank(parse("blue milton bottle"),[{**ITEM,"brand":None}])[0]["score"] == 81.25

def test_availability_ties_and_top_three():
 assert rank(parse("bottle"),[{**ITEM,"status":"returned"}]) == []
 assert [r["id"] for r in rank(parse("bottle"),[{**ITEM,"id":i} for i in [8,4,3,2]])] == [2,3,4]

def test_bfs_and_related_fallback():
 assert bfs("bottle") == {"bottle":0,"personalitems":1,"campusitem":2,"umbrella":2,"keys":2,"backpack":2}
 assert bfs("missing") == {}
 assert bfs("bottle",0) == {"bottle":0}
 related={**ITEM,"category":"umbrella"}
 assert rank(parse("bottle"),[related],True) == []
 assert rank(parse("blue milton bottle library star"),[related]) == []
 r=rank(parse("blue milton bottle library star"),[related],True)[0]
 assert r["related"] and r["score"] == 60 and not r["strong_candidate"]
 poor={**ITEM,"color":"red","brand":None,"mark":None,"location":"canteen"}
 assert rank(parse("blue milton bottle library star"),[poor,related],True) == []

def test_empty_query():
 assert rank(parse("something"),[ITEM]) == []

@pytest.mark.parametrize('text', ['', '   ', '!!!', 'not blue'])
def test_no_positive_evidence_never_ranks(text):
    assert parse(text)['positive'] == {}
    assert rank(parse(text), [ITEM]) == []


def test_alias_repetition_is_one_fact_not_ambiguity_or_extra_weight():
    query = parse('navy blue dark blue flask water bottle')
    assert query == {'positive': {'category': 'bottle', 'color': 'blue'},
                     'excluded': {}, 'ambiguous': []}
    result = rank(query, [ITEM])[0]
    assert result['denominator'] == 65
    assert result['coverage'] == 2
    assert result['reasons'] == {'category': 40, 'color': 25}


@pytest.mark.parametrize('text', [
    'blue not bottle', 'bottle not blue', 'bottle no milton',
    'bottle without library', 'bottle not star sticker',
])
def test_exclusions_apply_to_every_recognized_attribute(text):
    assert rank(parse(text), [ITEM]) == []


def test_exact_threshold_included_and_lower_score_excluded():
    query = parse('blue milton bottle library star')
    threshold = {**ITEM, 'color': 'red', 'brand': None, 'mark': None}
    below = {**threshold, 'id': 102, 'location': 'canteen'}
    result = rank(query, [below, threshold])
    assert [r['id'] for r in result] == [101]
    assert result[0]['score'] == 50
    assert result[0]['reasons'] == {'category': 40, 'color': 0, 'brand': 0, 'location': 10, 'mark': 0}


@pytest.mark.parametrize('query', ['blue milton', 'milton bottle', 'blue bottle'])
def test_strong_flag_requires_all_three_supplied_fields(query):
    result = rank(parse(query), [ITEM])[0]
    assert not result['strong_candidate']


def test_strong_flag_requires_agreement_not_just_supplied_fields():
    result = rank(parse('red milton bottle'), [ITEM])[0]
    assert not result['strong_candidate']


def test_unavailable_exact_item_does_not_block_related_fallback():
    returned = {**ITEM, 'status': 'returned'}
    related = {**ITEM, 'id': 102, 'category': 'umbrella'}
    result = rank(parse('blue milton bottle library star'), [returned, related], True)
    assert [r['id'] for r in result] == [102]
    assert result[0]['related'] and result[0]['reasons']['category'] == 0


def test_published_parser_limits_remain_visible():
    # Documented limitations, not a claim of general language understanding.
    assert parse('purple bottle')['positive'] == {'category': 'bottle'}
    assert rank(parse('purple bottle'), [ITEM])[0]['score'] == 100


def test_rank_is_repeatable_and_does_not_mutate_input():
    from copy import deepcopy
    query = parse('blue Milton bottle')
    items = [dict(ITEM)]
    before = deepcopy((query, items))
    assert rank(query, items) == rank(query, items)
    assert (query, items) == before


# --- plurals, slang, spelling suggestions, wider negation ---------------------

@pytest.mark.parametrize('text,expected', [
    ('bottles', 'bottle'), ('chargers', 'charger'), ('keys', 'keys'), ('key', 'keys'),
    ('watches', 'watch'), ('wallets', 'wallet'), ('id cards', 'idcard'),
])
def test_plurals_and_singulars_match_same_category(text, expected):
    assert parse(text)['positive'] == {'category': expected}


@pytest.mark.parametrize('text,expected', [
    ('bttl', 'bottle'), ('chgr', 'charger'), ('earbuds', 'earphones'),
    ('specs', 'glasses'), ('shades', 'glasses'), ('bagpack', 'backpack'),
])
def test_slang_and_short_forms(text, expected):
    assert parse(text)['positive'] == {'category': expected}


def test_slang_colors_and_brand_forms():
    assert parse('blk bttl')['positive'] == {'category': 'bottle', 'color': 'black'}
    assert parse('ray ban specs')['positive'] == {'category': 'glasses', 'brand': 'rayban'}


@pytest.mark.parametrize('text', ['not a blue bottle', 'not an navy bottle', 'no blue bottle',
                                  'not the blue bottle', 'without a blue bottle'])
def test_negation_reaches_past_articles(text):
    q = parse(text)
    assert q['excluded'] == {'color': ['blue']}
    assert q['positive'] == {'category': 'bottle'}
    assert rank(q, [ITEM]) == []
    assert [r['id'] for r in rank(q, [{**ITEM, 'color': 'red'}])] == [101]


def test_negation_does_not_leak_past_other_words():
    q = parse('not lost blue bottle')
    assert q['excluded'] == {} and q['positive']['color'] == 'blue'


def test_spelling_suggestion_is_offered_not_applied():
    from finder_core.engine import suggest_corrections, apply_correction
    assert parse('Miltn bottle')['positive'] == {'category': 'bottle'}
    fixes = suggest_corrections('Miltn bottle')
    assert fixes == [{'typed': 'miltn', 'suggestion': 'milton', 'field': 'brand'}]
    assert parse(apply_correction('Miltn bottle', 'miltn', 'milton'))['positive']['brand'] == 'milton'


@pytest.mark.parametrize('text', ['navy Milton flask near the library', 'lost my keys',
                                  'hello there', 'bottle left near hall', 'blue pen 2'])
def test_no_false_spelling_suggestions(text):
    from finder_core.engine import suggest_corrections
    assert suggest_corrections(text) == []


def test_common_typos_get_suggestions():
    from finder_core.engine import suggest_corrections
    got = {f['typed']: f['suggestion'] for f in suggest_corrections('bottel chrger umbrela')}
    assert got == {'bottel': 'bottle', 'chrger': 'charger'}
    assert parse('umbrela')['positive'] == {'category': 'umbrella'}


@pytest.mark.parametrize('text,category', [
    ('thing used for drinking water', 'bottle'),
    ('something for drinking', 'bottle'),
    ('writing instrument', 'pen'),
    ('something for writing', 'pen'),
    ('thing used to open doors', 'keys'),
    ('something for unlocking', 'keys'),
    ('rain protection', 'umbrella'),
    ('something for rainy days', 'umbrella'),
    ('bag used to carry books', 'backpack'),
    ('something to carry my books', 'backpack'),
])
def test_restored_vague_phrases(text, category):
    from finder_core.engine import parse_with_vague_matching
    from finder_core.vague_matching import match_vague_description
    assert match_vague_description(text) == [category]
    query = parse_with_vague_matching(text)
    assert query['positive']['category'] == category
    assert not query['ambiguous']
    result = rank(query, [{**ITEM, 'category': category}])[0]
    assert result['score'] == 100 and result['coverage'] == 1
