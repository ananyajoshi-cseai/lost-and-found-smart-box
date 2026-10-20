# Contributing to the Finder

Current source of truth: the simplified proposal and finder/PLAN.md. Work inside finder/; backend/, hardware/, frontend/ and older docs/ describe the archived Smart Box version.

## Start a task from current main

From the repository root, first run git status. If there are edits, commit or otherwise preserve them before switching branches; do not reset them away. Then:

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c finder/your-name-task
```

Replace the final name with a unique task branch, for example finder/anika-vocabulary, finder/ananya-rule-tests or finder/aashi-ui-review. Do not create new work from the old hardware/anika, backend/ananya or frontend/aashi snapshots. Those branches remain intact; nobody's branch is rewritten. If a proposed branch already exists, switch to it and inspect its history instead of recreating it.

For a new local checkout, clone the private repository using your own GitHub account, then follow finder/README.md. Never share account credentials. Collaborator access has already been arranged by the team lead.

## Review responsibilities

| Owner | Primary files | Review focus |
|---|---|---|
| Anika | finder_core/vocabulary.py, ontology.py, storage.py; data/items.seed.json | Knowledge, BFS, dataset and persistence |
| Ananya | finder_core/parser.py, scoring.py, engine.py; tests/ | Rules, contracts, tests and repository integration |
| Aashi | streamlit_app.py, views/; final evaluation/report | Interface, usability and honest measured results |

Paths in the table are relative to finder/. Existing starting implementations do not count as a teammate's authored contribution. Use genuine commits and explain inherited code honestly. Changes touching shared facts, labels or contracts should be reviewed by the affected teammate.

## Verify and submit

From finder/:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

From the repository root, inspect git diff and git status, stage only your intended files, commit with a concrete message, and push your task branch. Open a pull request into main, link the task issue and include the actual checks and remaining limitations. One teammate reviews before merge; this is a team rule, not a claim of configured branch protection. Do not force-push main or rewrite somebody else's branch.

Keep finder/CONTRACT.md synchronized with intentional data/function changes. No model training, ML/DL inference services, real personal records, runtime JSON or credentials in Git. Keep development examples separate from frozen final evaluation queries. A documentation-only change needs link/content review, not invented test results. Browser changes need relevant interface tests plus human usability review.

## Open task map

- Ananya: [reasoning and viva #1](https://github.com/ananyajoshi-cseai/lost-and-found-smart-box/issues/1).
- Anika: [knowledge/storage #4](https://github.com/ananyajoshi-cseai/lost-and-found-smart-box/issues/4).
- Aashi: [interface/evaluation #5](https://github.com/ananyajoshi-cseai/lost-and-found-smart-box/issues/5).
- Team: [integration/recovery #7](https://github.com/ananyajoshi-cseai/lost-and-found-smart-box/issues/7), then [final evidence #8](https://github.com/ananyajoshi-cseai/lost-and-found-smart-box/issues/8).

These existing issues were re-scoped after PR #14. Closed issues and the archive branch retain the old implementation history; superseded hardware gates were not falsely marked passed.
