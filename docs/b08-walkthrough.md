# B08: prepare evidence, explain the backend, finish the team gate

B08 in handbook page 29 depends on B01-B07. Fresh-install verification and evaluation are complete; final freeze waits for actual frontend/Wokwi acceptance and team review.

1. Read [evidence status](test-results/b08-status.md). Inspect the fresh-install results and distinguish backend verification from pending team acceptance.
2. Read [the backend report](report/person-b-backend.md). It covers the parser, BFS, weighted scoring, schema, claims, photos and recovery.
3. Rehearse [the viva exercise](demo/ananya-viva.md): derive a score, trace a queue and explain a retained failure aloud.
4. Repeat the documented fresh-install/test/evaluation commands when you rehearse or change code. Keep the v1 labels and engine unchanged.
5. Use [the frontend handoff](frontend-handoff.md) for interface integration. Resolve defects through reviewed changes and rerun affected checks.
6. Complete B07's actual team checklist. Only then agree the final commit/API snapshot and assemble the final team evidence. Issues #7 and #8 remain open.

This checkpoint changes documentation only. Existing API paths, schema, algorithms, dependencies and simulation-first plan remain unchanged. Report review remains pending.
