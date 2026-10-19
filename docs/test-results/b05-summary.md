# B05 evaluation: synthetic-v1

Measured on 19 October 2026. Evaluated code commit: `a8e33c99b87fb1f5a2f175e6d03b53cfdb0c046e`; dirty checkout: `False`. Full source and dataset SHA-256 hashes, UTC timestamp, individual API responses and 120 timing samples are preserved in [b05-evaluation-v1.json](b05-evaluation-v1.json).

## Results
| Metric | Measured result |
|---|---|
| Items / positive / negative queries | 20 / 12 / 6 |
| Top-1 hits | 12/12 (100%) |
| Top-3 success | 12/12 (100%) |
| Negative queries returning a candidate | 1/6 (16.67%) |
| Extra irrelevant cards across positive queries | 14 |
| Benchmark pool | 100 available synthetic records |
| Timed requests | 120, after 12 warm-up requests |
| Median / p95 / maximum | 3.21 / 4.64 / 34.46 ms |

All measured benchmark samples were below the handbook's 500 ms target. This only supports that target for the local in-process workload. TestClient includes SQLite, parsing/ranking and response validation; excludes browser/network time and photo retrieval. p95 uses nearest rank.

Machine: Windows-11-10.0.26200-SP0; Python 3.12.14; Intel64 Family 6 Model 186 Stepping 2, GenuineIntel; 12 logical CPUs. No hostname or personal data recorded.

## Interpret the limitations
The set is small and manually authored with knowledge of the existing design. These numbers are not campus accuracy, independent blind testing or evidence of generalization. The broadened umbrella case counts a correctly labelled related suggestion as relevant; it is not an exact umbrella match. A relevant first card does not mean every returned card is relevant.

The negative 'purple bottle' case returns non-purple bottles: the authored vocabulary ignores the unknown word purple. The failure is retained. No aliases, weights, threshold or broadening behavior were changed in response to evaluation. Future improvements require separate development examples and unchanged v1 reporting.

## Per-query evidence
| ID | Query | Relevant IDs | Returned IDs |
|---|---|---|---|
| q01 | navy Milton flask | [101, 109] | [101, 109, 102] |
| q02 | blue milton bottle library star | [101] | [101, 109, 102] |
| q03 | blue cello bottle canteen stripe | [102] | [102, 109, 101] |
| q04 | red milton bottle library | [103] | [103, 101, 109] |
| q05 | black notebook library star | [104] | [104, 118] |
| q06 | black keys library | [106] | [106, 116] |
| q07 | black charger canteen | [107] | [107, 114] |
| q08 | blue earphones library | [108] | [108, 115] |
| q09 | red notebook canteen stripe | [111] | [111] |
| q10 | blue pen library | [112] | [112, 119, 113] |
| q11 | bottle not blue | [103, 110, 120] | [103, 110, 120] |
| q12 | umbrella blue milton library star | [101] | [101, 109] |
| q13 | green wallet | [] | [] |
| q14 | purple bottle | [] | [101, 102, 103] |
| q15 | bottle not blue not red not black | [] | [] |
| q16 | notebook not black not red | [] | [] |
| q17 | umbrella | [] | [] |
| q18 | red blue bottle | [] | [] |

## Verification and handoff
The full automated suite passed: **50 passed, 1 warning in 5.77s**. The existing Starlette/httpx adapter deprecation warning remains; no warnings suppressed and no dependencies changed. Tests cover metrics arithmetic including empty groups, API/ranker parity, private-field exclusion, usable photo URLs, related labels, no-match/clarification behavior and isolation from existing data.

Aashi still needs to verify the new card fields in her UI. Claims, complete frontend integration, Wokwi and physical hardware remain outside this checkpoint. See [the B05 exercise](../b05-walkthrough.md).
