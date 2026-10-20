# Simplified scope and ownership

The software-only Campus Lost & Found Finder scope was adopted on 19 October 2026, based on the five-page project proposal. It replaces the original hardware/API plan.

## Keep / remove

Keep explicit knowledge, authored synonyms, negation/ambiguity rules, BFS depth two, supplied-field weighted scoring, human-readable explanations and honest evaluation. Remove the application dependency on devices, Wokwi, webcam/photos, FastAPI, SQLite, authentication, claims and purchases. Streamlit itself has web/data-library dependencies; their installation is not an ML feature or an external inference call.

The original version remains intact in the archive branch and historical folders. All new app imports stay within finder/; no backend app imports or HTTP calls are used for reasoning/storage. Existing teammate branches are not rewritten. To contribute, create a new feature branch from this simplified checkpoint after review/merge, so old code is not accidentally reintroduced.

## Anika — knowledge and storage

- Review the reused vocabulary, category graph, BFS trace and JSON contract.
- Review the 40 synthetic starter records; replace deliberate repeated-description pairs with useful realistic variations where appropriate.
- Extend categories/aliases toward the proposal's scope with tests using development examples, preserving frozen evaluation labels.
- Own add_item and mark_returned behavior, persistence validation and failure/restart checks.

## Ananya — reasoning and repository

- Reuse and adapt the parser/ranker contract; keep threshold 50, top three, weights 40/25/15/10/10 and depth-two fallback.
- Maintain algorithm, JSON and interface integration tests; review changes and preserve measured evidence.
- Explain one score, unsupported negation and a failure case. Do not present old backend evidence as new-app validation.

## Aashi — interface and evaluation

- Review and improve the three working starter pages and wording, including narrow-screen/keyboard checks.
- Create at least 15 frozen final queries (10 positive, 5 negative) against the agreed dataset; keep labels separate from the engine.
- Measure top-1, top-3 and negative false-positive rate without tuning against test labels.
- Assemble report/slides and rehearse the real report -> search -> return flow.

Changes are tracked through task branches and reviewed pull requests.

## Done gate

All three launch the simplified app; the persisted full flow works; corrupted storage errors remain visible; ambiguity/unknown words/related suggestions are handled honestly; final dataset and labels are frozen; measured results, limitations and human rehearsal are recorded. The original hardware/B07/B08 requirements are superseded by this scope.
