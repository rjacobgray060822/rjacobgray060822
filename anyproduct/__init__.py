"""AnyProduct Studio core package."""
from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("anyproduct")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.1.0"
