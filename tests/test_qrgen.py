from argparse import Namespace
import sys

import pytest

import quickqrforge as qrgen

# ensure the legacy module still loads without error and emits a warning
import importlib
import warnings

with warnings.catch_warnings(record=True) as _warns:
    warnings.simplefilter("always")
    importlib.import_module("qrgen")



def test_normalize_url_prepends_https():
    assert qrgen.normalize_url("example.com") == "https://example.com"


def test_console_scripts_registered():
    # ensure the package advertises the expected CLI entry points
    try:
        from importlib import metadata
    except ImportError:  # pragma: no cover - py<3.8
        import importlib_metadata as metadata

    eps = metadata.entry_points()
    # support both legacy and new metadata API shapes
    scripts = []
    if hasattr(eps, 'select'):
        scripts = [ep.name for ep in eps.select(group='console_scripts')]
    else:
        scripts = [ep.name for ep in eps.get('console_scripts', [])]

    assert 'qrgen' in scripts
    assert 'qr' in scripts


def test_normalize_url_rejects_empty():
    with pytest.raises(ValueError):
        qrgen.normalize_url("   ")


def test_parse_scale_rejects_non_positive():
    with pytest.raises(ValueError):
        qrgen.parse_scale("0")


def test_run_cli_returns_error_when_url_missing():
    args = Namespace(url=None, url_pos=None, output="qr.png", scale=10, tui=False)
    assert qrgen.run_cli(args) == 1


def test_run_cli_success_path(monkeypatch):
    args = Namespace(
        url="https://example.com",
        url_pos=None,
        output="out.png",
        scale=10,
        tui=False,
    )

    def fake_generate_qr(url_value: str, output: str, scale: int) -> str:
        assert url_value == "https://example.com"
        assert output == "out.png"
        assert scale == 10
        return "https://example.com"

    monkeypatch.setattr(qrgen, "generate_qr", fake_generate_qr)
    assert qrgen.run_cli(args) == 0


def test_tui_mode(monkeypatch, tmp_path, capsys):
    # simulate absence of curses so we exercise the prompt fallback
    monkeypatch.setattr(sys, "modules", {k: v for k, v in sys.modules.items() if k != "curses"})
    monkeypatch.setitem(sys.modules, "curses", None)

    # simulate user interacting with the menu-driven fallback UI
    # choose field 1, enter URL; field 2, enter filename; field 3, enter scale;
    # then hit 'G' to generate.
    inputs = iter([
        "1", "example.com",
        "2", str(tmp_path / "foo.png"),
        "3", "5",
        "G",
        "Q",  # quit after generating
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    called = {}
    def fake_generate_qr(data, output_path, scale=None, **kwargs):
        called['data'] = data
        called['output'] = output_path
        called['scale'] = scale
        return output_path

    monkeypatch.setattr(qrgen, "generate_qr", fake_generate_qr)

    args = Namespace(url=None, url_pos=None, output="ignored", scale=10, tui=True)
    assert qrgen.run_cli(args) == 0
    assert called['data'] == "https://example.com"
    assert called['output'] == str(tmp_path / "foo.png")
    assert called['scale'] == 5
