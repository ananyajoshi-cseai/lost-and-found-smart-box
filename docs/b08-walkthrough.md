# B08: prepare evidence, explain the backend, finish the team gate

B08 in handbook page 29 depends on B01-B07. We can prepare Ananya's report and viva material now, but final freeze waits for actual frontend/Wokwi acceptance and reproducible final measurements.

1. Read [evidence status](test-results/b08-status.md). Distinguish passed earlier checks from pending reruns.
2. Read [your report contribution](report/person-b-backend.md). It covers the parser, BFS, weighted scoring, schema, claims, photos and recovery.
3. Rehearse [the viva exercise](demo/ananya-viva.md): derive a score, trace a queue and explain a retained failure aloud.
4. Complete the fresh-install/test/evaluation commands in the evidence status. Keep the v1 labels and engine unchanged.
5. Use [the frontend handoff](frontend-handoff.md) to integrate with Aashi. Resolve defects through reviewed changes and rerun affected checks.
6. Complete B07's actual team checklist. Only then agree the final commit/API snapshot and assemble the final evidence with Aashi and Anika. Issues #7 and #8 remain open.

This checkpoint changes documentation only. Existing API paths, schema, algorithms, dependencies and simulation-first plan remain unchanged. Report text is ready for teammate review, not evidence that a teammate has reviewed it. No message has been sent to teammates.
