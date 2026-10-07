# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-10-07

### Added
- `geo.py`: `haversine_distance_meters()`
- `validation.py`: `validate_uuid()`, `validate_email()`, `validate_password()`
- `security.py`: `setup_security_headers()`, `check_production_security()`
- `notifications.py`: `send_email()`
- `plugins.py`: `discover_plugins(group)`
- `config.py`: `Settings` base class — construct via `Settings.load()`, not
  `Settings()` directly, so subclass-added fields get validated too

### Changed
- `fetch-buska-core` composite action now authenticates as a GitHub App
  (`app-client-id`/`app-private-key`) instead of a personal PAT (`token`) —
  consumers need to update their CI step and secrets accordingly

## [0.1.0] - 2026-09-04

### Added
- Initial package: typed exceptions (`exceptions.py`) and Flask error
  handlers (`error_handlers.py`)
- `transaction.py`: `transactional(session)` context manager
- Release workflow — pushing a `vX.Y.Z` tag builds a wheel/sdist and
  publishes it to a GitHub Release
- `fetch-buska-core` composite action for consumers to download the
  released wheel
