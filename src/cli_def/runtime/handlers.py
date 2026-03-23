# cli_def/runtime/handlers.py

from typing import Callable, Dict

_HANDLER_REGISTRY: Dict[str, Callable] = {}


def cli_def_handler(path: str):
    def decorator(func: Callable):
        _HANDLER_REGISTRY[path] = func
        return func
    return decorator


def get_registered_handler(path: str) -> Callable | None:
    return _HANDLER_REGISTRY.get(path)


def clear_registry():
    _HANDLER_REGISTRY.clear()