# QRGenerator

[![CI](https://github.com/Hibob555556/QRGenerator/actions/workflows/ci.yml/badge.svg)](https://github.com/Hibob555556/QRGenerator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/Hibob555556/QRGenerator?style=flat-square&v=2)](https://github.com/Hibob555556/QRGenerator/blob/main/LICENSE)


![TUI screenshot](images/screenshot.png)

Generate URL QR codes as PNG files using either:

- an interactive terminal UI (TUI), or
- a script-friendly command-line interface (CLI).

## Quick Start

```powershell
pip install -r requirements.txt
python .\qrgen.py https://example.com --output qr.png --scale 10
```

## Features

- Interactive TUI mode
- Non-interactive CLI mode for app/script integration
- URL normalization (`https://` auto-added when missing)
- Input validation and meaningful exit codes
- GitHub Actions CI and basic test coverage

## Installation

```powershell
git clone https://github.com/Hibob555556/QRGenerator.git
cd QRGenerator
pip install -r requirements.txt
```

## Usage

### TUI Mode

```powershell
python .\qrgen.py
```

Or:

```powershell
python .\qrgen.py --tui
```

### CLI Mode

Positional URL:

```powershell
python .\qrgen.py https://example.com
```

Flag-based URL:

```powershell
python .\qrgen.py --url https://example.com --output qr.png --scale 10
```

## CLI Arguments

- `url_pos` (optional positional): URL to encode
- `--url`: URL to encode (alternative to positional)
- `--output`: Output PNG file (default: `qr.png`)
- `--scale`: Positive integer image scale (default: `10`)
- `--tui`: Force interactive mode

## Exit Codes (CLI)

- `0`: success
- `1`: error (invalid input or generation failure)

## Development

Run tests:

```powershell
pytest -q
```

See:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
