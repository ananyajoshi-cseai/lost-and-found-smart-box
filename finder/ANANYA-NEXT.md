# Ananya: explain your Finder reasoning

Your reasoning code is implemented. This exercise is for understanding and reviewing it; a merged PR does not show that you personally completed it. Run commands from finder/ with its own .venv. No server, device key or staff password is needed.

## 1. Trace the parser

Read finder_core/vocabulary.py, then parser.py. Run:

```powershell
.\.venv\Scripts\python.exe -c "from finder_core.engine import parse; print(parse('navy Milton flask not red'))"
```

Expected positive facts: category=bottle, color=blue, brand=milton. Excluded color: red. Ambiguous: empty. Explain why navy/flask are aliases and why an unknown word contributes nothing.

Next try `red blue bottle` and `not a blue bottle`. The first has ambiguous color. The second exposes the limited immediate-negation rule: it does not understand the intervening word a. The interface asks users to check the interpretation rather than claiming full language understanding.

## 2. Derive a score before running it

Read scoring.py and the small proposal-format wrapper in engine.py. This command uses one temporary Python dictionary and changes no stored records:

```powershell
.\.venv\Scripts\python.exe -c "from finder_core.engine import parse,rank; item=dict(id=1,category='bottle',color='blue',brand='milton',location='library',mark='star',status='available'); print(rank(parse('blue Milton bottle canteen star'),[item]))"
```

Earned points: category 40 + color 25 + brand 15 + location 0 + mark 10 = 90. Supplied-weight denominator: 100. Score: 90; coverage: 5 of 5. Reasons are a field-to-points dictionary. The strong-candidate flag is true because category/color/brand agree, but it does not establish ownership.

Omit star from the query: 80/90*100 = 88.89 with coverage 4/5. Query only bottle: 40/40*100 = 100 with coverage 1/5. Explain why these scores cannot be compared as ownership probabilities.

## 3. Explain eligibility before scoring

Change the item's status to returned: rank returns an empty list. Use `bottle not blue`: the blue item is excluded regardless of its score. Use an ambiguous query: no guessing. With ties, returned score sorts descending then ID ascending; only the first three survive.

If an exact eligible category exists, related-category fallback is not used, even if those exact items later miss the score threshold. This is an important behavior to explain to Aashi.

## 4. Trace BFS with Anika

```powershell
.\.venv\Scripts\python.exe -c "from finder_core.engine import bfs; print(bfs('bottle'))"
```

Distances: bottle 0, personalitems 1, campusitem/umbrella/keys 2. Queue: bottle -> personalitems -> campusitem, umbrella, keys -> empty. Nodes at depth 2 are not expanded. This traverses category nodes, not item records. Related categories earn zero category points.

## 5. Run the existing edge-case tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_engine.py -q
```

Read one assertion for negation, one for ambiguity, one for ties and one for related fallback. Explain the failure each assertion would catch. Do not add tests just to increase the count or change expected outputs to conceal a defect.

## 6. Record your own evidence

In issue #1, record the commit you used, actual outputs, the tests you ran and anything you could not explain. Keep this exercise open until you can derive the score and queue without reading the answers. Next, review Anika's knowledge changes and Aashi's interface/evaluation against the shared contract.

Existing automated evidence remains in VERIFICATION.md. The inherited 18-query regression preserves the purple-bottle false positive; it does not replace Aashi's separate final evaluation of the agreed dataset.
