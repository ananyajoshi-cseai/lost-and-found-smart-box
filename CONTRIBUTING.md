# Contribution workflow

Use `hardware/anika`, `backend/ananya`, and `frontend/aashi`, or short task branches based on them. Before work: fetch origin and merge origin/main into your branch. Before a PR: run relevant checks, review git diff, commit only related files, and attach actual test evidence. Target `main`; one teammate reviews before merge. This is a documented team rule, not a claim that GitHub branch protection has been configured.

Ananya reviews interfaces/database, Anika circuit and device work, Aashi user workflows/docs. Keep routes and fields in docs/contracts.md synchronized. No credentials, real personal records, databases, private exports or upload images in Git. Use synthetic fixtures and explain limitations. No ML/DL dependencies or inference services.

Invite Anika and Aashi from Settings → Collaborators when their exact GitHub usernames are known. Role names are not guessed GitHub accounts; issues record human owners until then.
