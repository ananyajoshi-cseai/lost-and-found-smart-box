# AI decisions v1

Handbook pages 13-17 govern the engine. Facts are explicit strings; synonyms are manually authored. No training or image inference occurs.

Weights: category 40, color 25, brand 15, location 10, public mark 10. Score = 100 * matched weight / supplied positive weight; threshold 50, top 3, ties by integer ID ascending. Coverage is number of supplied attributes, not certainty. Blue Milton bottle/canteen/star against blue Milton bottle/library/star scores 90. Without the mark the denominator is 90 and the score is 88.89.

Rule order: unavailable exclusion; explicit negative exclusion; clarify ambiguity; exact-category pool; optional BFS only if exact pool empty; weighted score. Strong candidate means category/color/brand are supplied and equal, not proven ownership. Related categories earn zero category points.

BFS from bottle at depth 2: bottle:0, personalitems:1, campusitem/umbrella/keys:2. Search adjacency is bidirectional; logical IsA remains parent-directed. No DFS/A* claims.

Parser limits: English ASCII, punctuation boundaries, longest phrase first, immediate not/no/without only. 'not a blue bottle' has unsupported negation scope. Unknown/misspelled words contribute no evidence. Multi-color positives trigger clarification. Never silently autocorrect.

Implementation choices where companion files were absent: parsed object keys positive/excluded/ambiguous; deterministic sorted exclusion lists; response keys score/coverage/denominator/reasons/strong_candidate/related. Initial vocabulary is restricted to handbook examples. Expand values/aliases with tests and record rationale here. Unrounded score determines inclusion; returned score rounds to 2 decimals.

Unit tests are algorithm checks, not retrieval accuracy. A separate held-out evaluation set (10 positive, 5 negative queries; 15-20 items) and 100-item latency benchmark remain B05/B08 tasks. Do not report invented accuracy.

## B05 evaluation freeze
The v1 fixtures contain 20 items and 18 separately labelled queries (12 positive, 6 negative). They were authored with knowledge of the existing design but not used to tune it. They are a reproducible synthetic check, not an independent blind benchmark. No vocabulary, weight, threshold or broadening changes were made for B05.

The evaluation invokes POST /api/search with only query/broaden. Intended IDs stay in the evaluator. Top-1 and Top-3 count successful positive queries once each; empty output is a miss. Negative false-positive rate counts negative queries returning any candidate. Zero denominators produce null. Per-query responses retain unrelated cards even when the query gets a relevant hit.

The 100-item speed test uses available copies of the fixture facts with unique IDs. It times the full in-process TestClient request with perf_counter, including database access and response validation; it excludes startup, warm-up, network/browser and photo retrieval. Median, nearest-rank p95, maximum and every sample are recorded. It measures a synthetic local workload, not deployed or multi-user performance.
