# cli_def/runtime/handlers.py
from __future__ import annotations

from typing import Callable, Iterable,  Any, Mapping, Sequence
from dataclasses import dataclass

_EARLY_BINDING_HANDLER_REGISTRY: dict[str, Callable] = {}
_ALL_HANDLERS_CATALOG: dict[str, list[CliHandlerMeta]] = {}


@dataclass
class CliHandlerMeta:
    path: str
    module: str
    name: str
    tags: set[str]|None = None
    description: str|None = None
    late_binding: bool = False

    @property
    def entrypoint(self) -> str:
        return f"{self.module}:{self.name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "module": self.module,
            "name": self.name,
            "tags": list(self.tags) if self.tags else [],
            "description": self.description,
            "late_binding": self.late_binding,
            "entrypoint": self.entrypoint,
        }


def cli_def_handler(
        path: str,
        *,
        late_binding: bool = False,
        tags: Iterable[str]|None = None,
        description: str|None = None,
        ) -> Callable[[Callable], Callable]:

    def decorator(func: Callable):
        meta = CliHandlerMeta(
            path=path,
            module=func.__module__,
            name=func.__name__,
            tags=set(tags) if tags else None,
            description=description,
            late_binding=late_binding,
        )
        _ALL_HANDLERS_CATALOG.setdefault(path, [])
        _ALL_HANDLERS_CATALOG[path].append(meta)
        if not late_binding:
            _EARLY_BINDING_HANDLER_REGISTRY[path] = func
        return func
    return decorator


def get_registered_handler(path: str) -> Callable | None:
    return _EARLY_BINDING_HANDLER_REGISTRY.get(path)


def clear_registry():
    _EARLY_BINDING_HANDLER_REGISTRY.clear()


def get_all_handlers_catalog() -> Mapping[str, Sequence[CliHandlerMeta]]:
    return _ALL_HANDLERS_CATALOG


def clear_all_handlers_catalog():
    _ALL_HANDLERS_CATALOG.clear()

