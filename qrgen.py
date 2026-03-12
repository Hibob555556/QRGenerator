"""Backwards-compatibility shim for the old ``qrgen`` module.

The real implementation now lives in :mod:`quickqrforge` and this module
re-exports everything while emitting a deprecation warning.  Existing users can
continue importing ``qrgen`` without immediate breakage, but they should switch
in their code to the new name.
"""

from __future__ import annotations

import warnings

# re-export everything from the new module so that ``from qrgen import ...``
# continues to work.
from quickqrforge import *  # noqa: F401, F403

# re-declare __all__ so that ``import *`` behaves consistently.
from quickqrforge import __all__  # type: ignore

warnings.warn(
    "The 'qrgen' module is deprecated; use 'quickqrforge' instead.",
    DeprecationWarning,
    stacklevel=2,
)
