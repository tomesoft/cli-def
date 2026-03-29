# cli_def/runtime/dispatcher.py
from typing import Callable, Mapping, Any, Sequence
import importlib
import argparse
import logging

from .event import CliEvent
from ..models import (
    CliDef,
    ExecutableNode,
    CommandDef,
    MultDef,
)

from .handlers import get_registered_handler
from .context import CliRuntimeContext
from .result import HandlerResult

# --------------------------------------------------------------------------------
# Dispatcher class
# --------------------------------------------------------------------------------
class CliDispatcher:

    def __init__(self, cli_def: CliDef, fallback_handler: Callable[[CliEvent], Any] = None):
        self.cli_def : CliDef = cli_def
        self.fallback_handler : Callable[[CliEvent], Any] = fallback_handler or type(self)._default_fallback_handler
        self._handler_cache: dict[str, Callable] = {}
        self._pre_load_entrypoints()

    @staticmethod
    def _default_fallback_handler(event: CliEvent):
        print("[fallback handler of Dispatcher]")
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
            self._resolve_handler_entrypoint(entrypoint)


    def dispatch(
            self,
            args: argparse.Namespace,
            extra_args: Sequence[str] = None,
            ctx: CliRuntimeContext = None,
            ) -> Any: # args: argparse.Namespace
        event = self._build_event(args, extra_args=extra_args, ctx=ctx)
        handler = self._resolve_handler(event.command) or self.fallback_handler
        result = handler(event)
        return self.normalize_result(result, event)


    # called via click binder
    def _dispatch(
            self,
            defpath: str,
            kwargs: dict[str, Any],
            extra_args: Sequence[str] = None,
            ctx: CliRuntimeContext = None,
            ) -> Any:
        logging.debug(f"@@@ Dispatcher._dispatcher called {defpath}")
        command = self.cli_def.find(defpath)
        if command is None:
            raise RuntimeError(f"Command not found from defpath: [{defpath}]")
        params = self._normalize(command, dict(kwargs))
        event = CliEvent(
            path=defpath,
            command=command,
            params=params,
            event_source=self,
            extra_args=extra_args,
            ctx=ctx,
        )
        handler = self._resolve_handler(event.command) or self.fallback_handler
        result =  handler(event)
        return self.normalize_result(result, event)


    def _build_event(
            self,
            args: argparse.Namespace,
            extra_args: Sequence[str] = None,
            ctx: CliRuntimeContext = None,
            ):
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
            ctx=ctx,
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

            # unbox if mult definition is (1,1)
            if mult.is_fixed and mult.lower == 1:
                if isinstance(v, list):
                    result[k] = v[0] if v else None
                else:
                    result[k] = v
            else:
                result[k] = v

        return result

    def _resolve_handler(self, command: CommandDef):
        path = command.defpath  # "MyCLI/command1"

        handler = get_registered_handler(path)
        if handler:
            logging.debug(f"handler found in registry: {path}")
            return handler

        if command.entrypoint:
            return self._resolve_handler_entrypoint(command.entrypoint)

        logging.debug(f"handler NOT found {path} -> fallback")
        return self.fallback_handler


    def _resolve_handler_entrypoint(self, handler_str: str) -> Callable | None:
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


    def normalize_result(self, result: Any, event: CliEvent) -> HandlerResult:
        if result is None:
            return HandlerResult(defpath=event.command.defpath)

        if isinstance(result, HandlerResult):
            return result

        return HandlerResult(
            defpath=event.command.defpath,
            data=result
        )