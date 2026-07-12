"""Generator discovery and loading utilities."""
from __future__ import annotations

import importlib
import inspect
import pkgutil
from functools import lru_cache
from typing import Dict, Iterable, Mapping, Type

from .generators import Generator


def _iter_generator_modules() -> Iterable[str]:
    package_name = "anyproduct.generators"
    package = importlib.import_module(package_name)
    try:
        package_path = package.__path__  # type: ignore[attr-defined]
    except AttributeError:  # pragma: no cover - namespace packages only
        return

    for module_info in pkgutil.iter_modules(package_path):
        name = module_info.name
        if name.startswith("_") or name == "base":
            continue
        yield f"{package_name}.{name}"


@lru_cache()
def get_registry() -> Mapping[str, Type[Generator]]:
    """Return a mapping of generator slug -> class."""

    registry: Dict[str, Type[Generator]] = {}
    for module_name in _iter_generator_modules():
        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not issubclass(obj, Generator) or obj is Generator:
                continue
            if not obj.slug:
                continue
            registry[obj.slug] = obj
    return registry


def get_generator(slug: str) -> Type[Generator]:
    registry = dict(get_registry())
    if slug not in registry:
        raise KeyError(f"Unknown generator '{slug}'")
    return registry[slug]


def available_generators() -> Iterable[Type[Generator]]:
    return get_registry().values()
