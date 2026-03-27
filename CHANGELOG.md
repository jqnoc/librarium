# Changelog

All notable changes to Librarium will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-03-27

### Added
- Electron shell wrapping the Flask backend — the app now opens in its
  own window instead of requiring a browser.
- Dynamic port allocation: Flask binds to a random free port, eliminating
  port-conflict issues.
- Custom application menu with Reload, Quit, standard Edit operations,
  and zoom controls.
- External links open in the default browser instead of inside the app.
- `APP_VERSION` constant in `app.py`, exposed to all templates via the
  `app_version` context variable.
- `CHANGELOG.md` (this file).
- `package.json` with Electron dev dependency and build configuration.
- `main.js` — Electron main process (spawns Flask, manages window lifecycle).
- `preload.js` — sandboxed preload exposing `window.librarium.isElectron`.

### Changed
- `app.py` startup block now reads `LIBRARIUM_PORT` and `LIBRARIUM_ELECTRON`
  environment variables; debug mode is disabled when running under Electron.
- `run-librarium.bat` updated to launch via Electron (`npm start`).
- Footer in `base.html` now displays the app version.

[0.1.0]: https://github.com/librarium/librarium/releases/tag/v0.1.0
