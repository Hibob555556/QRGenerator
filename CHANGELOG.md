# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Released]

### Added 1.0

- Interactive TUI mode for QR generation.
- Non-interactive CLI mode for scripting and app integration.
- Input validation and URL normalization.
- Initial project documentation and repository metadata files.

### Changed 1.1

- Package renamed internally to ``quickqrforge`` (module and import path).
  ``qrgen`` module now a compatibility shim emitting a deprecation warning.
- Updated documentation and tests to use new name.
- Added short alias CLI script ``qr`` and ensured entry points continue
  working after rename.
