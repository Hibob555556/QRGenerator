"""Core logic and public API for the QuickQRForge package.

During the renaming of the project the original implementation lived in the
``qrgen`` module.  To avoid breaking users that imported ``qrgen`` we moved
all functionality into this file, kept a thin shim in ``qrgen.py`` that simply
re-exports everything, and added a deprecation warning.

This module exposes both programmatic helpers (``create_qr_image`` and
``generate_qr``) and a command‑line driver including a terminal user
interface.  The CLI can operate in one of two modes:

* a curses-based full screen form, if the standard library ``curses`` module is
  available; or
* a menu-driven prompt implementation that works even on vanilla Windows.

The expectation is that most downstream code will either call ``generate_qr``
directly or execute the ``qrgen``/``qr`` console script, but the helpers are
useful for testing and embedding.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Union

import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

# Mapping user-visible error correction letters to the constants used
# by ``qrcode``.  The table is intentionally unexported; callers should pass
# the letter and we perform validation ourselves.
_ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def create_qr_image(
    data: str,
    *,
    error_correction: str = "M",
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
):
    """Return a Pillow ``Image`` representing ``data`` encoded as a QR.

    Parameters mirror those accepted by the underlying ``qrcode`` library.  We
    perform minimal validation (non-empty ``data`` and a recognized
    ``error_correction`` letter) and raise :class:`ValueError` on misuse.

    This helper is the smallest unit of functionality and is used both by the
    CLI and programmatic consumers.
    """
    if not data:
        raise ValueError("`data` must be a non-empty string.")

    level = _ERROR_LEVELS.get(error_correction.upper())
    if level is None:
        raise ValueError("`error_correction` must be one of: L, M, Q, H.")

    qr = qrcode.QRCode(
        version=None,
        error_correction=level,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color=fill_color, back_color=back_color)


def normalize_url(url: str) -> str:
    """Sanitize and normalise an input URL for QR encoding.

    Many users enter bare domains; this function trims whitespace, rejects an
    empty value, and prefixes ``https://`` if neither scheme is present.

    ``generate_qr`` and the CLI depend on this behaviour to guarantee the
    payload is a valid URL-like string.

    Raises :class:`ValueError` if ``url`` is empty or contains only
    whitespace.
    """
    if not url or not url.strip():
        raise ValueError("URL must be a non-empty string.")
    url = url.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return url


def parse_scale(scale: Union[str, int]) -> int:
    """Normalize the ``--scale``/``scale`` CLI parameter to an int.

    The CLI accepts a numeric argument; programmatic callers may also supply
    an integer.  We ensure the returned value is positive, raising
    :class:`ValueError` for invalid input.  This logic is shared between the
    TUI and non‑TUI command processing.
    """
    if isinstance(scale, int):
        if scale <= 0:
            raise ValueError("scale must be a positive integer")
        return scale
    try:
        value = int(scale)
    except Exception:
        raise ValueError("scale must be an integer")
    if value <= 0:
        raise ValueError("scale must be a positive integer")
    return value


def run_cli(args: argparse.Namespace) -> int:
    """Run the command-line flow using parsed options.

    This function is mostly a thin wrapper around :func:`main` but takes an
    ``argparse.Namespace`` object directly, which makes it convenient for
    unit tests.  It returns the integer exit code that would be returned from
    a ``main()`` invocation.
    """
    # if the user explicitly asked for the TUI, hand off
    if args.tui:
        return run_tui()

    url = args.url_pos or args.url
    if not url:
        return 1
    try:
        url = normalize_url(url)
    except ValueError:
        return 1
    try:
        scale = parse_scale(args.scale)
    except ValueError:
        return 1
    try:
        # pass scale through to ``generate_qr`` (which treats it as
        # ``box_size`` internally)
        generate_qr(url, args.output, scale=scale)
    except Exception:
        return 1
    return 0


def generate_qr(
    data: str,
    output_path: str | Path,
    *,
    scale: int | None = None,
    error_correction: str = "M",
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
) -> Path:
    """Create a QR code image and write it to the filesystem.

    ``data`` is the payload to encode.  ``output_path`` may be a string or
    :class:`pathlib.Path` – the routine will create parent directories as
    needed and return a resolved ``Path`` to the written file.

    The keyword-only arguments mirror those in :func:`create_qr_image`, with
    the addition of ``scale`` which exists for backwards compatibility with
    earlier releases of the package (it maps directly to ``box_size``).

    This is the workhorse used by both the CLI and any external Python code.
    """
    # allow callers to specify ``scale`` for backwards compatibility
    if scale is not None:
        box_size = scale

    image = create_qr_image(
        data=data,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        fill_color=fill_color,
        back_color=back_color,
    )
    out = Path(output_path).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    # PIL.Image.save accepts a filename or a file object; stubs are overly
    # strict, so convert to str and silence the type checker.
    filename = str(out)  # type: ignore[assignment]
    image.save(filename)  # type: ignore[argument]   
    return out


def generate_qr_code(
    data: str,
    filename: str | Path,
    *,
    error_correction: str = "M",
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
) -> Path:
    """Backward-compatible alias for programmatic consumers."""
    return generate_qr(
        data=data,
        output_path=filename,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        fill_color=fill_color,
        back_color=back_color,
    )


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the :mod:`argparse` parser used by the CLI.

    The returned parser understands both positional and flag-based URLs, an
    output filename, image scale, error correction level, and a ``--tui``
    switch.  Mutual exclusion is enforced between the positional and
    ``--url`` arguments for clarity.
    """
    parser = argparse.ArgumentParser(description="Generate a QR code image.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("url_pos", nargs="?", help="URL to encode (positional)")
    group.add_argument("--url", help="URL to encode (alternative to positional)")

    parser.add_argument(
        "-o",
        "--output",
        default="qrcode.png",
        help="Output file path (default: qrcode.png).",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=10,
        help="Image scale (box size in pixels, default: 10).",
    )
    parser.add_argument(
        "--error-correction",
        default="M",
        choices=sorted(_ERROR_LEVELS.keys()),
        help="Error correction level: L, M, Q, or H (default: M).",
    )
    parser.add_argument("--border", type=int, default=4, help="Border width in modules.")
    parser.add_argument("--fill-color", default="black", help="Foreground color.")
    parser.add_argument("--back-color", default="white", help="Background color.")
    parser.add_argument("--tui", action="store_true", help="Force interactive mode.")
    return parser



# helper used for the fallback prompt-based TUI when curses is unavailable

def _prompt_tui() -> int:
    # provide a simple textual menu when curses isn't available; this
    # mirrors the screen shown in the repository screenshots but uses only
    # print/input so it works on any interpreter (Windows included).
    fields = {"URL": "", "Filename": "qr.png", "Scale": "10"}
    msg = "Ready."

    while True:
        print("""
==================================================
QR Code Generator
==================================================
Edit fields, then generate the PNG.
""")
        for idx, (name, value) in enumerate(fields.items(), start=1):
            print(f"[{idx}] {name} : {value}")
        print("[G] Generate QR")
        print("[O] Generate + Open")
        print("[Q] Quit")
        print(msg)
        choice = input("Select option: ").strip().upper()

        if choice in ("1", "2", "3"):
            key = list(fields.keys())[int(choice) - 1]
            new = input(f"Enter {key}: ").strip()
            if new:
                fields[key] = new
        elif choice in ("G", "O"):
            try:
                url_norm = normalize_url(fields["URL"])
                scale = parse_scale(fields["Scale"])
                out = generate_qr(
                    data=url_norm,
                    output_path=fields["Filename"],
                    scale=scale,
                )
                msg = f"QR code saved to: {out}"
                if choice == "O":
                    try:
                        import webbrowser
                        webbrowser.open(str(out))
                    except Exception:
                        pass
            except Exception as exc:
                msg = f"error: {exc}"
        elif choice == "Q":
            return 0
        # loop back for another command


def run_tui() -> int:
    """Launch the terminal user interface and return an exit code.

    This entry‑point is invoked whenever the user requests ``--tui`` or runs
    the program with no arguments.  It tries to import ``curses`` and, if the
    import succeeds, runs a lightweight form-driven UI.  On platforms without
    curses (notably default Windows installations) we gracefully fall back to
    a text‑based menu implemented in :func:`_prompt_tui` so that the feature
    works everywhere without additional dependencies.
    """
    try:
        import curses
    except ImportError:
        return _prompt_tui()

    def _curses_main(stdscr):
        # menu-driven screen similar to the old UI screenshot
        curses.curs_set(0)
        fields = {"URL": "", "Filename": "qr.png", "Scale": "10"}
        msg = "Ready."

        def redraw():
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            stdscr.addstr(0, 0, "=" * w)
            title = "QR Code Generator"
            stdscr.addstr(1, max(0, (w - len(title)) // 2), title)
            stdscr.addstr(2, 0, "=" * w)
            stdscr.addstr(4, 2, "Edit fields, then generate the PNG.")
            line = 6
            for i, (name, value) in enumerate(fields.items(), start=1):
                stdscr.addstr(line, 2, f"[{i}] {name} : {value}")
                line += 1
            line += 1
            stdscr.addstr(line, 2, "[G] Generate QR")
            stdscr.addstr(line + 1, 2, "[O] Generate + Open")
            stdscr.addstr(line + 2, 2, "[Q] Quit")
            stdscr.addstr(line + 4, 2, msg)
            stdscr.addstr(line + 6, 2, "Select option: ")
            stdscr.refresh()

        while True:
            h, w = stdscr.getmaxyx()
            redraw()
            ch = stdscr.getkey()
            if ch in ("1", "2", "3"):
                key = list(fields.keys())[int(ch) - 1]
                curses.echo()
                prompt = f"Enter {key}: "
                stdscr.addstr(h - 2, 2, " " * (w - 4))
                stdscr.addstr(h - 2, 2, prompt)
                stdscr.refresh()
                val = stdscr.getstr(h - 2, 2 + len(prompt), 200).decode().strip()
                curses.noecho()
                if val:
                    fields[key] = val
            elif ch.upper() in ("G", "O"):
                # attempt generation
                try:
                    url_norm = normalize_url(fields["URL"])
                    scale = parse_scale(fields["Scale"])
                    out = generate_qr(
                        data=url_norm,
                        output_path=fields["Filename"],
                        scale=scale,
                    )
                    msg = f"QR code saved to: {out}"
                    if ch.upper() == "O":
                        try:
                            import webbrowser
                            webbrowser.open(str(out))
                        except Exception:
                            pass
                except Exception as exc:
                    msg = f"error: {exc}"
                stdscr.getch()
            elif ch.upper() == "Q":
                # user chose to quit without generating; treat as success
                return 0
            # loop back and redraw

    try:
        return curses.wrapper(_curses_main)
    except Exception:
        # if curses initialization fails for whatever reason, fall back
        return _prompt_tui()


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point exposed by the console script.

    ``argv`` may be supplied for testing; if omitted ``argparse`` will read
    from :data:`sys.argv`.  The function returns an exit code suitable for
    passing to ``sys.exit()``.
    """
    args = build_parser().parse_args(argv)
    # explicit TUI request takes precedence
    if args.tui:
        return run_tui()

    # prefer flag over positional
    url = args.url or args.url_pos
    if not url:
        print("error: URL required", file=sys.stderr)
        return 1
    try:
        url = normalize_url(url)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        scale = parse_scale(args.scale)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out = generate_qr(
        data=url,
        output_path=args.output,
        scale=scale,
        error_correction=args.error_correction,
        border=args.border,
        fill_color=args.fill_color,
        back_color=args.back_color,
    )
    print(f"QR code saved to: {out}")
    return 0



__all__ = [
    "build_parser",
    "create_qr_image",
    "generate_qr",
    "generate_qr_code",
    "normalize_url",
    "parse_scale",
    "run_cli",
    "run_tui",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
