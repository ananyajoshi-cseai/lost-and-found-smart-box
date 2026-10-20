# Person B report: deterministic reasoning

Prepared for the simplified Campus Lost & Found Finder. This section describes the implemented local Python reasoning, not the archived FastAPI/IoT project. It can be incorporated into the team report after review.

## Inputs and knowledge

Found items are explicit facts in JSON: category, color, optional brand, location, optional public mark and availability. Authored vocabulary maps synonyms to canonical facts, for example navy to blue and flask to bottle. No model is trained, images are not analyzed, and no external inference service is called. Knowledge/vocabulary and the category graph are Anika's review responsibility; the reasoning functions consume them.

## Parsing and inference rules

parse(text) lowercases and tokenizes ASCII letter/digit sequences. Within each attribute it tries longer phrases before shorter ones, preventing water bottle or dark blue from being double-counted. Immediate not/no/without before a recognized phrase adds a canonical value to exclusions. Multiple positive values for one field, or a value both positive and negative, produce ambiguity. Repeated aliases for the same canonical value are a single fact.

The output has positive, excluded and ambiguous fields. Unknown tokens add no evidence. No known positive attributes or ambiguity means no ranked results; the UI asks for detail or clarification. The engine filters non-available items and any attribute matching an exclusion before calculating scores. Thus a perfect text match cannot override returned status or a negated color.

## Heuristic ranking

Weights are category 40, color 25, brand 15, location 10 and public mark 10. Only supplied positive fields contribute to the denominator:

score = 100 * sum(matching supplied weights) / sum(all supplied positive weights)

Missing or mismatching item values earn zero points for that supplied field. Exclusions filter candidates rather than contributing points. Keep unrounded scores >=50, return scores rounded to two decimals, sort by returned score descending then integer item ID ascending, and return at most three records. No training or automatic weight optimization is performed.

Example query: blue Milton bottle, canteen, star. Item: blue Milton bottle, library, star. Earned points are 40+25+15+0+10=90 out of 100, so score=90 and coverage=5/5. Without star in the query, earned weight=80 and denominator=90, so score=88.89 and coverage=4/5. With only bottle supplied, 40/40 gives 100 with coverage=1/5. Coverage must therefore accompany the score. A score is agreement on stated facts, never ownership probability.

The returned reasons dictionary maps supplied fields to earned points. strong_candidate is true only when category, color and brand are all supplied and all agree. It is a display label, not permission to return an item. Staff independently verifies the return in the supervised demo.

## Integration with BFS

With a supplied category, the engine first selects eligible exact-category items. Only if this pool is empty and the user enables related categories does it call Anika's depth-two BFS over the category graph. Returned/excluded exact-category items do not block fallback; existing eligible exact items do, even if they later fail the score threshold. Related categories earn zero category points and are visibly labelled.

The graph search uses a queue and a visited-distance map. From bottle: bottle at 0, personalitems at 1, then campusitem/umbrella/keys at 2. Depth-two nodes are not expanded. This is graph traversal over categories, not searching database records. The UI calls parse/rank directly; no HTTP transport or SQLite is involved.

## Validation and limits

Automated cases cover aliases, punctuation, longest phrases, all three immediate negation words, exclusions across all five attributes, conflicting facts, empty/negative-only input, exact threshold, omitted fields, unavailable items, strong-candidate requirements, stable ties, related fallback and repeatability without input mutation. JSON and interface integration tests cover the wider report/search/return flow. Exact run results are in ANANYA-HANDOFF.md.

The retained limitations are authored English/ASCII vocabulary, no spelling correction and limited negation scope. Purple bottle can return other-colored bottles because purple is unknown. Not a blue bottle is not handled like bottle not blue. These failures remain documented; no final evaluation labels were changed to conceal them.

The inherited frozen regression uses 20 items and 18 queries and previously returned 12/12 positive top-1/top-3 hits with 1/6 negative false positives. It is not independent evaluation of the 40-item starter dataset or campus accuracy. Aashi owns the separate final labelled evaluation and must record its actual results. Existing automated tests do not establish personal viva rehearsal or teammate review.
