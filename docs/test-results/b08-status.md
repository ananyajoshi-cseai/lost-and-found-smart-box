# B08 backend evidence checkpoint

Measured 19 October 2026 against clean commit `ac8d9356f6ae6c7ed8955f4ea625b43f223581e0`. This commit adds documentation to merged PR #12; application code and dependencies are unchanged from that merged backend. B07 genuine-client acceptance and the team rehearsal remain pending. No final release tag or team API freeze is declared.

## Reproducibility and review

| Check | Actual evidence/status |
|---|---|
| Fresh checkout | Separate local Git clone with no hardlinks; clean working tree recorded by evaluator |
| Fresh environment | New Python 3.12.14 virtual environment; pip installed all 25 pinned requirements, using cached package downloads where available |
| Dependency consistency | pip check: No broken requirements found |
| Full automated suite | 86 passed, 1 existing Starlette/httpx deprecation warning, 20.67 seconds; temporary synthetic databases |
| API snapshot | Parsed docs/openapi.json equals app.openapi(); no contract drift detected |
| Score/BFS examples | Direct engine calls produced scores 90.0 and 88.89; bottle:0, personalitems:1, campusitem/umbrella/keys:2 |
| Documentation | New relative links and git diff --check passed |
| No-ML dependency/source review | Inspected pinned requirements, authored parser/ontology/scoring and network-use references; no ML/DL/inference dependency or call identified |
| Credential/storage review | .env.example contains empty values; credentials come from environment; tracked-file scan found no .db/.jpg/.png/.pem/.key or secret-named file. Test credentials are disposable synthetic fixtures. This is a scoped source review, not a full-history secret scan or vulnerability audit |
| Genuine Wokwi, browser acceptance and team rehearsal | Pending; backend fixtures cannot pass these gates |

The initial restricted checkout attempt failed; the first escalation was not executed because approval review reached an account usage limit. A later approved retry completed installation and verification successfully. Partial scratch material from the failed attempt is outside the deliverable and was not used for these measurements.

## Frozen synthetic-v1 retrieval evaluation

[Raw B08 report](b08-evaluation-v1.json) preserves the commit, clean flag, timestamp, machine, source/dataset SHA-256 hashes, all query responses and all timing samples. Labels, authored vocabulary, weights, threshold and broadening logic were not tuned for this run. The fixture JSON content matches the prior B05 dataset.

| Metric | Result |
|---|---:|
| Items / positive / negative queries | 20 / 12 / 6 |
| Top-1 hits | 12/12 |
| Top-3 success | 12/12 |
| Negative queries returning candidates | 1/6 (16.67%) |
| Extra irrelevant cards across positives | 14 |
| Benchmark pool | 100 available synthetic records |
| Timed requests after 12 warm-ups | 120 |
| Median / nearest-rank p95 / maximum | 6.71 / 8.65 / 14.49 ms |

All measured samples were below 500 ms for this in-process workload. This is not browser/network/photo-download latency or multi-user performance. The set was manually authored with knowledge of the design and is not a blind campus benchmark. Positive-query success does not mean every returned card is relevant or prove ownership. The retained negative failure is purple bottle: unknown purple is ignored, so other-colored bottles can appear. The broadened umbrella case counts an explicitly labelled related suggestion as relevant.

Machine: Windows-11-10.0.26200-SP0; Python 3.12.14; Intel64 Family 6 Model 186 Stepping 2, GenuineIntel; 12 logical CPUs. No hostname, personal records, RAM or laptop model is inferred. Earlier timings remain in [B05 results](b05-summary.md); elapsed-time differences between these runs are not evidence of a code performance change.

## Repeat the checks

Use a new checkout folder, follow backend/README.md to create a new environment and install requirements, then from backend:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe evaluation.py --output ../docs/test-results/b08-evaluation-repeat.json
```

Run evaluation before changing tracked files so its commit/dirty flag are interpretable. Choose a new output filename each time. Record actual install/test results, preserve raw results, and never retune against these frozen labels. These commands use temporary synthetic databases. Final team release still requires the actual frontend/Wokwi workflow, teammate review and Ananya's oral rehearsal.
