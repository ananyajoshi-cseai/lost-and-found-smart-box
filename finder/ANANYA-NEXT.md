# Reasoning examples

Runnable examples for the Finder parser, ranking rules and graph traversal. Run commands from finder/ with its .venv. No server, device key or staff password is needed.

## 1. Trace the parser

Read finder_core/vocabulary.py, then parser.py. Run:

```powershell
.\.venv\Scripts\python.exe -c "from finder_core.engine import parse; print(parse('navy Milton flask not red'))"
```

Expected positive facts: category=bottle, color=blue, brand=milton. Excluded color: red. Ambiguous: empty. Navy/flask are canonical aliases; unknown words contribute no facts.

Next try `red blue bottle` and `not a blue bottle`. The first has ambiguous color. The second exposes the limited immediate-negation rule: it does not understand the intervening word a. The interface asks users to check the interpretation rather than claiming full language understanding.

## 2. Score calculation

Read scoring.py and the small proposal-format wrapper in engine.py. This command uses one temporary Python dictionary and changes no stored records:

```powershell
.\.venv\Scripts\python.exe -c "from finder_core.engine import parse,rank; item=dict(id=1,category='bottle',color='blue',brand='milton',location='library',mark='star',status='available'); print(rank(parse('blue Milton bottle canteen star'),[item]))"
```

Earned points: category 40 + color 25 + brand 15 + location 0 + mark 10 = 90. Supplied-weight denominator: 100. Score: 90; coverage: 5 of 5. Reasons are a field-to-points dictionary. The strong-candidate flag is true because category/color/brand agree, but it does not establish ownership.

Omit star from the query: 80/90*100 = 88.89 with coverage 4/5. Query only bottle: 40/40*100 = 100 with coverage 1/5. These scores measure supplied-fact agreement, not ownership probability.

## 3. Eligibility rules

Change the item's status to returned: rank returns an empty list. Use `bottle not blue`: the blue item is excluded regardless of its score. Use an ambiguous query: no guessing. With ties, returned score sorts descending then ID ascending; only the first three survive.

If an exact eligible category exists, related-category fallback is not used, even if those exact items later miss the score threshold. The interface follows this fallback behavior.

## 4. BFS trace

```powershell
.\.venv\Scripts\python.exe -c "from finder_core.engine import bfs; print(bfs('bottle'))"
```

Distances: bottle 0, personalitems 1, campusitem/umbrella/keys 2. Queue: bottle -> personalitems -> campusitem, umbrella, keys -> empty. Nodes at depth 2 are not expanded. This traverses category nodes, not item records. Related categories earn zero category points.

## 5. Run the existing edge-case tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_engine.py -q
```

The test suite covers negation, ambiguity, score arithmetic, ties and related-category fallback.

## 6. Verification records

Verification records include the tested commit, commands, actual results and unresolved defects. Contract changes require integration review.

Existing automated evidence remains in VERIFICATION.md. The inherited 18-query regression preserves the purple-bottle false positive; it does not replace the separate final evaluation of the agreed dataset.
