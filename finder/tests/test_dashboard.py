from finder_core.dashboard import counts, radar_svg


def test_chart_counts_include_each_record_once():
    rows = [{'color':'blue'}, {'color':'blue'}, {'color':'red'}]
    assert counts(rows, 'color') == [{'Label':'Blue','Items':2}, {'Label':'Red','Items':1}]
    assert counts([], 'color') == []


def test_radar_distinguishes_missing_evidence_from_mismatch():
    svg = radar_svg({'reasons': {'category': 40, 'color': 0}})
    assert svg.count('>Not supplied</text>') == 3
    assert svg.count('>Mismatch</text>') == 1
    assert svg.count('>Match</text>') == 1
    assert 'nan' not in svg.lower()
