# AGENTS.md

Instructions for AI coding agents working in this repository. Read this first;
follow links for anything deeper rather than expecting it duplicated here.

## What this is

buska-core: the shared core package for BusKá backends (`municipal-backend`,
`corporate-backend`). Background IP, owned by BusKá — see
[`ARQUITETURA_REPOSITORIOS.md`](https://github.com/BusKa-org/corporate-backend/blob/main/ARQUITETURA_REPOSITORIOS.md)
§2 and §5 for the ownership rule and the test for what does/doesn't belong
here. Consumers install a released wheel directly (no package index) — see
[`README.md`](README.md) for the release/consumption mechanics.

## Running things

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check buska_core tests
uv run black --check buska_core tests
uv run mypy buska_core
```

## Conventions

- Nothing segment-specific belongs here — not municipal's fixed-route
  scheduling, not PaqTcPB's DRT engine. `ARQUITETURA_REPOSITORIOS.md` §5 has
  the "every plausible future client needs this" test to run before moving
  anything into this package.
- Extraction only ever sources from `municipal-backend`, never
  `corporate-backend` — anything in `corporate-backend` since its
  2026-08-03 fork is presumptively Foreground IP (PaqTcPB-owned) until
  confirmed otherwise.
- New public surface is designed for subclassing/extension where a consumer
  might plausibly need a field/behavior the others don't (see
  `Settings.load()` in `config.py`), not copied over as a closed class.
- Go easy on comments/docstrings — state the non-obvious rationale, not an
  essay restating what the code already says.

## Writing PR descriptions

Written for a reviewer with no chat context — a brief for someone deciding
whether to approve, not a changelog of what you did. Four sections, in this
order, every time:

- **Contexto** — why this PR exists, 1-3 sentences. Link the
  `ARQUITETURA_REPOSITORIOS.md` section it implements when there is one. If
  stacked on another PR, say which one, and which commit in the branch is
  actually new vs. already merged elsewhere.
- **O que mudou** — bullets, one per module/concern, not a paragraph. A
  table beats prose for before/after numbers (test counts, line counts).
- **Por quê** — the reasoning the diff alone can't show: why this approach
  over an alternative, what was dropped from the original and why, what was
  deliberately left out.
- **Como testar** — what ran (`pytest`, `mypy`, etc.) and what it proves.

A sentence running past ~3 lines is a sign it should be a bullet or a table
row instead. `.github/PULL_REQUEST_TEMPLATE.md` has the skeleton.

## Before opening a PR

- [ ] `black --check`, `ruff check`, `mypy`, `pytest -q` all pass
- [ ] `README.md`'s "What's in here" table and "Status" section updated if
      a module was added or moved
- [ ] PR description follows `.github/PULL_REQUEST_TEMPLATE.md` (Contexto /
      O que mudou / Por quê / Como testar)
