# B08 backend evidence status

Prepared 19 October 2026. Current merged code: `0626bb8e63cf0ae677026df05fb12826912b1231` (PR #12). This is a preparation checkpoint; B07 team acceptance and the B08 fresh-install/evaluation rerun are not complete. No final release tag or API freeze is declared.

| Check | Actual evidence/status |
|---|---|
| B07 automated backend suite | 86 passed, 1 existing Starlette/httpx deprecation warning, 11.05 seconds on Windows/Python 3.12.14, before documentation-only edits in code commit 6363a224c2ea0e7c42912b7561821baf75219812 |
| B07 GitHub validation | Backend tests run 39206049763 succeeded for PR #12; workflow installs pinned requirements on Ubuntu/Python 3.12 and runs pytest |
| Fresh local checkout and environment for B08 | Not completed: initial sandbox attempt failed; escalated fresh-clone/install request was not executed because automatic approval review hit an account usage limit |
| Fresh B08 suite and labelled evaluation | Pending; no new measurement claimed |
| Previous labelled retrieval evaluation | B05 code a8e33c99b87fb1f5a2f175e6d03b53cfdb0c046e, clean checkout; raw report linked below |
| No-ML dependency/source review | Inspected pinned requirements, authored parser/ontology/scoring and network-use references; no ML/DL/inference dependency or call identified |
| Credential/storage review | .env.example contains empty variable values; runtime credentials come from environment; tracked-file scan found no .db/.jpg/.png/.pem/.key or secret-named file. Synthetic credentials in tests are disposable fixtures. This is a scoped source review, not a full history secret scan or vulnerability audit |
| Algorithm/schema report and viva answers | Drafted in docs/report/person-b-backend.md and docs/demo/ananya-viva.md |
| Genuine Wokwi, browser acceptance and team rehearsal | Pending; backend fixtures cannot pass these gates |

[GitHub B07 run](https://github.com/ananyajoshi-cseai/lost-and-found-smart-box/actions/runs/39206049763). [B05 raw report](b05-evaluation-v1.json) includes source/dataset hashes, timestamp, CPU/OS/Python, responses and all timings. [B05 interpretation](b05-summary.md) retains failures.

## Previously measured results; not a B08 rerun

20 synthetic items, 12 positive and 6 negative queries. Top-1 12/12, top-3 12/12; negative false positives 1/6 (purple bottle); 14 extra irrelevant cards across positives. The 100-record in-process benchmark measured 120 requests after warm-up: median 3.21 ms, nearest-rank p95 4.64 ms, maximum 34.46 ms. It excludes browser/network/photo-download time. Dataset authors knew the design; this is not a blind campus benchmark.

Machine recorded in that report: Windows-11-10.0.26200-SP0; Python 3.12.14; Intel64 Family 6 Model 186 Stepping 2, GenuineIntel; 12 logical CPUs. Do not infer RAM, laptop model or current-run measurements from this metadata.

## Reproduce the pending checks

Use a new checkout folder, follow backend/README.md to create a new virtual environment and install requirements, then from backend:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe evaluation.py --output ../docs/test-results/b08-evaluation-v1.json
```

Run evaluation before changing tracked files so its recorded commit and dirty flag are interpretable. Preserve the report's dataset/source hashes, every query result and timing sample. Use a new filename if one already exists. Do not tune rules or labels after looking at results. Record actual install/test output and machine details, then update this status using those results. Tests and evaluation create temporary synthetic databases and do not require real claim data.

The local interrupted attempt created only partial scratch material under work/b08-clean; it is not an installed checkout and is not part of the deliverable.

Documentation verification: ran the existing parser/ranker/BFS directly for the viva examples; observed scores 90.0 and 88.89 and distances bottle:0, personalitems:1, campusitem/umbrella/keys:2. New documentation relative links and git diff --check passed. These focused checks do not replace the pending full B08 rerun.
