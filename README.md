# Campus Lost & Found Finder

Current direction: a **software-only, rule-based AI semester project** using Python, Streamlit and JSON. No IoT, model training, inference service, images, FastAPI application, login or claim workflow is required to run it.

## Start here

Open [finder/README.md](finder/README.md) for setup, launch and the report -> search -> return exercise. The new application is entirely inside `finder/`.

- [Agreed simplified scope and team tasks](finder/PLAN.md)
- [Pure Python function/data contract](finder/CONTRACT.md)
- [Migration and verification evidence](finder/VERIFICATION.md)

Ananya owns reasoning/tests and repository integration; Anika owns knowledge/storage/BFS; Aashi owns interface/evaluation/report. The initial simplified scaffold reuses existing work and supplies working starting implementations for all three. It is not evidence that teammates have authored or reviewed those modules. Each person should now review, test, extend and explain her component in her own commits.

## Original Smart Box version

The completed original checkpoint is preserved on `archive/smart-box-v1` at `06e9f37`. The existing `backend/`, `hardware/`, `frontend/` and older `docs/` are historical material and are not used by the Finder application. Their old endpoints, role checklists and measurements do not describe the new app. Do not install or launch them for the simplified demo.

The 5-page Campus Lost & Found Finder proposal replaces the original handbook for the current direction, following Ananya's instruction on 19 October 2026. The private repository name is retained to avoid disrupting collaborators. Course approval for dropping IoT is not claimed.
