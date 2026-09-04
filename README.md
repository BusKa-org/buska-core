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

## Using this package

```bash
uv add buska-core  # once published; for now, a path or git dependency
```

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
