from argparse import Namespace

import pytest

import qrgen


def test_normalize_url_prepends_https():
    assert qrgen.normalize_url("example.com") == "https://example.com"


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
