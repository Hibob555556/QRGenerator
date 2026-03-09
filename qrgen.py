import argparse
import os
import sys
from typing import Optional
from pathlib import Path

import pyqrcode


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("URL cannot be empty.")
    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"
    return value


def parse_scale(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise ValueError("Scale must be a positive integer.")
    return parsed


def generate_qr(url_value: str, output: str, scale: int) -> str:
    final_url = normalize_url(url_value)
    final_scale = parse_scale(str(scale))
    if not output.strip():
        raise ValueError("Output file cannot be empty.")

    qr = pyqrcode.create(final_url)
    qr.png(output, scale=final_scale)
    return final_url


def open_file(path: str) -> None:
    resolved = Path(path).resolve()
    if os.name == "nt":
        os.startfile(str(resolved))  # type: ignore[attr-defined]
        return
    # Fallbacks for non-Windows terminals.
    import subprocess

    if sys.platform == "darwin":
        subprocess.run(["open", str(resolved)], check=True)
    else:
        subprocess.run(["xdg-open", str(resolved)], check=True)


def draw_ui(url: str, output: str, scale: str, status: Optional[str] = None) -> None:
    clear_screen()
    print("=" * 58)
    print(" " * 19 + "QR Code Generator")
    print("=" * 58)
    print(" Edit fields, then generate the PNG.")
    print()
    print(f"  [1] URL      : {url or '<empty>'}")
    print(f"  [2] Filename : {output}")
    print(f"  [3] Scale    : {scale}")
    print()
    print("  [G] Generate QR")
    print("  [O] Generate + Open")
    print("  [Q] Quit")
    print("-" * 58)
    print(f" {status}" if status else " Ready.")


def main() -> None:
    url = ""
    output = "qr.png"
    scale = "10"
    status: Optional[str] = None

    while True:
        draw_ui(url, output, scale, status)
        choice = input("\nSelect option: ").strip().lower()

        try:
            if choice == "1":
                url = input("Enter URL: ").strip()
                status = "URL updated."
            elif choice == "2":
                new_output = input("New output filename (e.g. qr.png): ").strip()
                if not new_output:
                    raise ValueError("Output filename cannot be empty.")
                output = new_output
                status = "Output filename updated."
            elif choice == "3":
                new_scale = input("Scale (positive integer): ").strip()
                parse_scale(new_scale)
                scale = new_scale
                status = "Scale updated."
            elif choice == "g":
                final_url = generate_qr(url, output, int(scale))
                status = f"Saved QR code to '{output}' from '{final_url}'."
            elif choice == "o":
                final_url = generate_qr(url, output, int(scale))
                open_file(output)
                status = f"Saved and opened '{output}' from '{final_url}'."
            elif choice == "q":
                break
            else:
                status = "Invalid option. Choose 1, 2, 3, G, O, or Q."
        except ValueError as exc:
            status = f"Input error: {exc}"
        except Exception as exc:  # pragma: no cover
            status = f"Failed to generate QR code: {exc}"

    clear_screen()
    print("Goodbye.")


def run_cli(args: argparse.Namespace) -> int:
    try:
        url_value = args.url or args.url_pos
        if not url_value:
            raise ValueError("CLI mode requires a URL. Use --url or pass a positional URL.")

        final_url = generate_qr(url_value, args.output, args.scale)
        print(f"Saved QR code to '{args.output}' from '{final_url}'.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate QR code PNG files.")
    parser.add_argument("url_pos", nargs="?", help="URL to encode (positional form).")
    parser.add_argument("--url", help="URL to encode in the QR code.")
    parser.add_argument("--output", default="qr.png", help="Output PNG file path.")
    parser.add_argument(
        "--scale",
        type=int,
        default=10,
        help="PNG scale (positive integer).",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch interactive TUI mode.",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.tui:
        main()
    elif args.url or args.url_pos:
        raise SystemExit(run_cli(args))
    else:
        main()
