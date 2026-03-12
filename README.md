# QuickQRForge

[![CI](https://github.com/Hibob555556/QRGenerator/actions/workflows/ci.yml/badge.svg)](https://github.com/Hibob555556/QRGenerator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/Hibob555556/QRGenerator?style=flat-square&v=2)](https://github.com/Hibob555556/QRGenerator/blob/main/LICENSE)

![TUI screenshot](images/screenshot.png)

Generate URL QR codes as PNG files using either:

- an interactive terminal UI (TUI), or
- a script-friendly command-line interface (CLI).

> The CLI is exposed via the `qrgen` command once the package is installed
> from PyPI; no additional setup is necessary.

## Quick Start

```powershell
pip install QuickQRForge
# after installing you can use either the full name or the short alias
qrgen https://example.com --output qr.png --scale 10
# or simply
qr https://example.com --output qr.png --scale 10
```

## Features

- Interactive TUI mode
- Non-interactive CLI mode for app/script integration
- URL normalization (`https://` auto-added when missing)
- Input validation and meaningful exit codes
- GitHub Actions CI and basic test coverage

## Installation

Install from PyPI (dependencies are handled automatically):

```powershell
pip install QuickQRForge
```

> After installation a cross‑platform `qrgen` executable script will be placed
> on your PATH, allowing you to run the utility directly from the shell.

Optional: install/upgrade to the latest release:

```powershell
pip install --upgrade QuickQRForge
```

## Usage

### TUI Mode

By default the command launches a simple screen-based interface using the
standard library ``curses`` module.  You can tab between fields and press
Enter when finished – it looks like a little form rather than a sequence of
prompts.

If ``curses`` isn't available (for example, on stock Windows installs) the
package gracefully falls back to a line-by-line prompt instead; no additional
dependencies are required, though installing ``windows-curses`` will enable
the full screen UI on Windows.

```powershell
qrgen        # or: qrgen --tui
```

### CLI Mode

Positional URL:

```powershell
qrgen https://example.com
```

Flag-based URL:

```powershell
qrgen --url https://example.com --output qr.png --scale 10
```

## Example Usage

Generate `qr.png` from a URL using defaults:

```powershell
qrgen https://example.com
```

Generate a QR code with a custom file name and scale:

```powershell
qrgen https://openai.com --output openai-qr.png --scale 12
```

Use the flag-based URL argument (useful in scripts):

```powershell
qrgen --url https://github.com --output github.png --scale 8
```

Start in interactive TUI mode:

```powershell
qrgen --tui
```

## Use in Python Code

The library can be imported directly in Python.  The public API originally
lived in the ``qrgen`` module, but the package was renamed and the canonical
import path is now ``quickqrforge``.  The old module still exists and issues a
``DeprecationWarning`` when imported, so you can update at your leisure.

```python
import quickqrforge as qrf

qrf.generate_qr("https://example.com", "example.png")
```

You can still use the CLI via ``subprocess`` if you prefer:

```python
import subprocess

subprocess.run([
    "qrgen", "https://example.com", "--output", "example.png", "--scale", "12"
], check=True)
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

Install from source:

```powershell
git clone https://github.com/Hibob555556/QRGenerator.git  # repo name remains for now
cd QRGenerator   # directory name unchanged after clone
pip install -e .
```

Run tests:

```powershell
pytest -q
```

See:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
