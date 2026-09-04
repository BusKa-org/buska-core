# buska-core

The shared core for BusKá backends. Background IP, owned by BusKá — see
`ARQUITETURA_REPOSITORIOS.md` in
[`BusKa-org/corporate-backend`](https://github.com/BusKa-org/corporate-backend/blob/main/ARQUITETURA_REPOSITORIOS.md)
for the architecture this package implements and the rule for what does and
doesn't belong here (§5).

## What's in here

| Module | Extracted from | Contains |
|---|---|---|
| `buska_core/exceptions.py` | `municipal-backend/app/core/exceptions.py` | Typed application exceptions (`NotFoundError`, `ValidationError`, `ForbiddenError`, `UnauthorizedError`, `ConflictError`) |
| `buska_core/error_handlers.py` | `municipal-backend/app/core/error_handlers.py` | `register_error_handlers()` and `register_jwt_handlers()` — a consistent HTTP error contract for any Flask app built on this package |
| `buska_core/transaction.py` | `municipal-backend/app/core/transaction.py` | `transactional(session)` — commit/rollback context manager. Takes a `Session` explicitly instead of importing a project's global `db`, so this package doesn't need to own or assume any app's SQLAlchemy instance |

Extraction sources only ever `municipal-backend`, never `corporate-backend` —
anything touched inside `corporate-backend` since its 2026-08-03 fork was
modified under the PaqTcPB-funded engagement and is presumptively Foreground
IP until confirmed otherwise (ARQUITETURA_REPOSITORIOS.md §2).

## What does NOT belong here

Nothing segment-specific. Not municipal's fixed-route scheduling, not
PaqTcPB's DRT engine. See ARQUITETURA_REPOSITORIOS.md §5 for the full rule.

## Releases

Pushing a `vX.Y.Z` tag runs `.github/workflows/release.yml`: tests, lints,
builds a wheel + sdist, and attaches them to a GitHub Release. No package
index involved — see "Using this package" below for why.

## Using this package

Consumers install a specific released wheel directly, not from a package
index — there's no PyPI listing and no self-hosted index server to run.

`.github/actions/fetch-buska-core` in this repo is the one copy of the
"download a release wheel into `./vendor`" logic. Each consumer:

- Pins a version in a `.buska-core-version` file at its repo root (just
  the tag, e.g. `v0.1.0`) — the single source of truth for that consumer's
  buska-core version, read by both `make fetch-buska-core` (local dev,
  also a dependency of `install`/`install-dev`/`docker-build`) and CI.
- In CI, calls the shared action instead of keeping its own script,
  authenticating as a GitHub App installed on this repo (Contents:
  Read-only) rather than a personal PAT — see "Authenticating CI" below:
  ```yaml
  - name: "Fetch buska-core"
    uses: BusKa-org/buska-core/.github/actions/fetch-buska-core@main
    with:
      app-client-id: ${{ secrets.BUSKA_CORE_APP_CLIENT_ID }}
      app-private-key: ${{ secrets.BUSKA_CORE_APP_PRIVATE_KEY }}
  ```
  (the action reads `.buska-core-version` itself when `version` isn't
  given explicitly)
- Points `[tool.uv.sources]` at the downloaded wheel file for uv, and has
  its Dockerfile `pip install` it directly before `pip install -e .`.

See either backend's `Makefile`, `pyproject.toml`, and `Dockerfile` for
the exact wiring.

Bumping the version a consumer uses means updating two places there: its
`.buska-core-version` file and the wheel filename in `[tool.uv.sources]`.

### Authenticating CI

Consumer CI reads this repo's releases via a GitHub App, not a personal
fine-grained PAT — a PAT is always someone's individual credential, so
access breaks (or has to be silently re-issued under someone else's
account) if that person leaves or their account is suspended. An App is
an org-owned identity instead. One-time setup (org admin):

1. **Settings → Developer settings → GitHub Apps → New GitHub App**, under
   BusKa-org. Any name/homepage URL works; uncheck "Active" under Webhook
   (not needed). Under "Repository permissions", set **Contents:
   Read-only** — nothing else.
2. "Where can this GitHub App be installed?" → **Only on this account**.
3. Create the app, then generate a private key on its settings page
   (downloads a `.pem` file) and note the **Client ID** shown there.
4. **Install** the app (from its settings page, "Install App") onto
   BusKa-org, selecting only the `buska-core` repository.
5. In each consumer repo's **Settings → Secrets and variables →
   Actions**, add `BUSKA_CORE_APP_CLIENT_ID` (the Client ID) and
   `BUSKA_CORE_APP_PRIVATE_KEY` (the full `.pem` contents).

CI then mints a token scoped only to this repo, valid for about an hour,
on every run — nothing long-lived is stored beyond the App's own key.

```python
from flask import Flask
from flask_jwt_extended import JWTManager
from buska_core.error_handlers import register_error_handlers, register_jwt_handlers

app = Flask(__name__)
register_error_handlers(app)
jwt = JWTManager(app)
register_jwt_handlers(jwt)
```

## Development

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check buska_core tests
uv run black --check buska_core tests
uv run mypy buska_core
```

## Status

Step 2 of the migration plan in `ARQUITETURA_REPOSITORIOS.md` §6 — exceptions,
error handlers, and the transaction context manager have landed. RBAC/authz,
tenancy (`Organizacao`), geo primitives, notifications, and the
plugin-discovery mechanism are still to come; most of those need real
genericization work (e.g. `authz.py` is currently coupled to
municipal-backend's `User`/`Gestor` models) rather than a straight copy.
