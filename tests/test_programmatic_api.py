from pathlib import Path

import quickqrforge as qrgen

# keep the old import path available for compatibility; silence the
# deprecation warning since tests already know about it.
import importlib
import warnings
with warnings.catch_warnings(record=True):
    warnings.simplefilter("ignore", DeprecationWarning)
    importlib.import_module("qrgen")


def test_create_qr_image_returns_image():
    image = qrgen.create_qr_image("https://example.com")
    assert hasattr(image, "save")


def test_generate_qr_writes_file(tmp_path: Path):
    output = tmp_path / "out.png"
    result = qrgen.generate_qr("hello world", output)
    assert result == output.resolve()
    assert output.exists()
