# AI + IoT Lost-and-Found Smart Box

A simulation-first college prototype using explicit facts, rules, ontology BFS and heuristic ranking. **No ML, deep learning, embeddings, vision model or external inference API.** Photos support human verification; a score never proves ownership.

## Team
| Owner | Responsibility | Branch |
|---|---|---|
| Anika Aggarwal | Wokwi, ESP32, hardware and capture | `hardware/anika` |
| Ananya Joshi | Repository, Python AI, FastAPI and SQLite | `backend/ananya` |
| Aashi Srivastava | HTML/CSS/JS, acceptance tests and documentation | `frontend/aashi` |

## Current checkpoint
Implemented: virtual environment, `/health`, five-table schema, device authentication, idempotent events, staff pending events, parser, ontology/BFS, heuristic ranking database-backed search, item registration, sanitized JPEG storage public item views, complete search cards a reproducible synthetic evaluation runner, public claim submission and staff-only atomic decisions with audit. Automated tests exercise these components.

B07 backend integration is implemented: `/ui` hosting, restricted optional local CORS, tested replay-to-return HTTP flow, and offline database-plus-photo recovery. Not yet implemented: the frontend and real Wokwi circuit; full team acceptance remains open. Their contracts and issues are prepared. Do not present this checkpoint as a complete product or a passed hardware gate.

Start with [Ananya's walkthrough](docs/start-here-ananya.md), then [backend commands](backend/README.md). See [API contract](docs/contracts.md), [AI decisions](docs/ai-decisions.md), and [contribution workflow](CONTRIBUTING.md).

## Structure
- `backend/app/`: routes, AI, schema and services
- `backend/tests/`: isolated API/database and algorithm tests
- `frontend/`: Aashi's browser interface workspace
- `hardware/simulation/`: serial replay bridge and synthetic event
- `hardware/firmware/`, `hardware/wiring/`: Anika's later physical implementation
- `docs/`: contracts, learning steps, evidence and report assets

## Simulation-first launch order
1. Start the local backend using `backend/README.md`.
2. Anika implements the handbook page 8 trigger in Wokwi and saves a serial event.
3. Replay the same JSON twice; expect 201 then 200 and only one pending event.
4. Register one item using /docs and find it through search (see docs/b04-walkthrough.md).
5. Buy parts only after the handbook's simulation gate passes. Wokwi networking to laptop localhost is not assumed.

The 39-page handbook dated 18 October 2026 is the source of truth. See `docs/source-of-truth.md` for provenance and specification gaps. The repository name differs from its example by explicit team-lead choice.

For B05, follow [search and evaluation walkthrough](docs/b05-walkthrough.md). The evaluation uses temporary data and keeps every query result, including failures.

For B06, use the [claim-and-decision walkthrough](docs/b06-walkthrough.md). Public claims stay pending until staff verifies ownership; a match score never approves a return.

For B07, follow the [integration and recovery walkthrough](docs/b07-walkthrough.md). The backend suite has 86 passing tests; actual frontend and Wokwi acceptance are still pending.

For B08, use the [backend evidence and viva preparation](docs/b08-walkthrough.md). Report sections, handoff instructions and fresh-install/test/evaluation evidence are prepared; final team acceptance remains pending.
