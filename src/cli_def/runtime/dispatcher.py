# cli_def/runtime/dispatcher.py
from typing import Callable, Mapping, Any, Sequence
import importlib

from .event import CliEvent
from ..models import (
    CliDef,
    ExecutableNode,
    CommandDef,
    MultDef,
)

class Dispatcher:

    def __init__(self, cli_def: CliDef, fallback_handler: Callable = None):
        self.cli_def = cli_def
        self.fallback_handler = fallback_handler or type(self).default_fallback_handler
        self._handler_cache: dict[str, Callable] = {}
        self._pre_load_entrypoints()

    @staticmethod
    def default_fallback_handler(event):
        print("[fallback handler]")
        print("  PATH:", event.path)
        print("  PARAMS:", event.params)
        if event.extra_args:
            print("  EXTRA:", event.extra_args)


    def _pre_load_entrypoints(self):
        executables = self.cli_def.select_all(
            lambda node: isinstance(node, ExecutableNode)
            and node.entrypoint is not None
        )
        entrypoints = {node.entrypoint for node in executables}
        for entrypoint in entrypoints:
            self._resolve_handler(entrypoint)


    def dispatch(self, args, extra_args: Sequence[str] = None) -> Any: # args: argparse.Namespace
        event = self._build_event(args, extra_args=extra_args)
        handler = self._resolve_handler(event.command.entrypoint) or self.fallback_handler
        return handler(event)


    def _build_event(self, args, extra_args: Sequence[str] = None):
        command = getattr(args, "_command", None)
        path = getattr(args, "_path", None)

        if command is None or path is None:
            raise RuntimeError("No command metadata found")

        params = {
            k: v for k, v in vars(args).items()
            if not k.startswith("_") and (
                k not in ("_path", "_command", "command"))
        }

        params = self._normalize(command, params)

        event = CliEvent(
            path=path,
            command=command,
            params=params,
            event_source=self,
            extra_args=list(extra_args) if extra_args else None,
        )

        return event


    def _normalize(self, command: CommandDef, params: Mapping[str, Any]):
        result = {}

        # key → ArgumentDef のマップ作る
        arg_map = {arg.key: arg for arg in command.arguments}

        for k, v in params.items():
            arg = arg_map.get(k)

            if arg is None:
                result[k] = v
                continue

            mult: MultDef = arg.mult

            # 👇 ここが本質
            if mult.is_fixed and mult.lower == 1:
                if isinstance(v, list):
                    result[k] = v[0] if v else None
                else:
                    result[k] = v
            else:
                result[k] = v

        return result


    def _resolve_handler(self, handler_str: str):
        if handler_str is None:
            return None

        # at first find in cache
        if handler_str in self._handler_cache:
            return self._handler_cache[handler_str]

        module_path, func_name = handler_str.split(":")
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            raise RuntimeError(f"Failed to load handler: {handler_str}")

        func = getattr(module, func_name)
        if func is None:
            raise RuntimeError(f"Failed to load handler: {handler_str}")

        self._handler_cache[handler_str] = func
        return func
        