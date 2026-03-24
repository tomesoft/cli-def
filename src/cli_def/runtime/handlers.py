# cli_def/runtime/handlers.py

from typing import Callable, Dict, List, Iterable, Optional
from dataclasses import dataclass
import pkgutil
import importlib

_EARLY_BINDING_HANDLER_REGISTRY: Dict[str, Callable] = {}
_ALL_HANDLERS_CATALOG: Dict[str, List[HandlerMeta]] = {}

@dataclass
class HandlerMeta:
    path: str
    module: str
    name: str
    tags: Optional[set[str]] = None
    description: Optional[str] = None
    late_bindings: bool = False

    @property
    def entrypoint(self) -> str:
        return f"{self.module}:{self.name}"


def cli_def_handler(
        path: str, *,
        late_bindings: bool = False,
        tags: Iterable[str] = None,
        description: str = None,
        ) -> Callable[[Callable], Callable]:
    def decorator(func: Callable):
        meta = HandlerMeta(
            path=path,
            module=func.__module__,
            name=func.__name__,
            tags=set(tags) if tags else None,
            description=description,
            late_bindings=late_bindings,
        )
        _ALL_HANDLERS_CATALOG.setdefault(path, [])
        _ALL_HANDLERS_CATALOG[path].append(meta)
        if not late_bindings:
            _EARLY_BINDING_HANDLER_REGISTRY[path] = func
        return func
    return decorator


def get_registered_handler(path: str) -> Callable | None:
    return _EARLY_BINDING_HANDLER_REGISTRY.get(path)


def clear_registry():
    _EARLY_BINDING_HANDLER_REGISTRY.clear()

def get_all_handlers_catalog() -> Dict[str, List[HandlerMeta]]:
    return _ALL_HANDLERS_CATALOG


def scan_handlers(package_path: str):
    module = importlib.import_module(package_path)
    import_all_modules(module)
    return get_all_handlers_catalog()


def import_all_modules(package):
    for _, name, _ in pkgutil.walk_packages([package.__name__], package.__name__ + "."):
        importlib.import_module(name)