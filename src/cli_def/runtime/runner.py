# cli_def/runtime/runner.py
from __future__ import annotations
from typing import Sequence, Iterable, Any, Callable, TYPE_CHECKING, Tuple

import sys
import argparse
import logging

from ..models import CliDef
from ..backend.argparse import ArgparseBuilder
from ..ops import dump_cli_def_pretty


from .dispatcher import CliDispatcher
from .context import CliRuntimeContext
from .event import CliEvent
from .result import (
    HandlerResult,
    ResultKind,
    CliResult,
)
from .utils import (
    make_runtime_context,
    setup_logging,
)
if TYPE_CHECKING:
    from .session import CliSession

class CliRunner:

    def __init__(
            self,
            cli_def: CliDef,
            fallback_handler: Callable[[CliEvent], HandlerResult|None]|None = None,
            *,
            default_backend: str="argparse",
            default_ctx: CliRuntimeContext|None = None,
            session: CliSession|None = None,
            ):
        self.cli_def = cli_def
        self.fallback_handler = fallback_handler
        self.default_backend = default_backend
        self.backend: str|None = None
        self.default_ctx = default_ctx
        self.session = session

        self.ctx: CliRuntimeContext|None = None
        self.builder: ArgparseBuilder = ArgparseBuilder()
        self.dispatcher: CliDispatcher = CliDispatcher(self.cli_def, fallback_handler=self.fallback_handler)


    def run(self, argv: Iterable[str]| str | None = None) -> CliResult:
        argv = self._normalize_argv(argv)

        early_args, remaining = self._early_parse(argv)
        self.ctx = self._make_context(early_args)

        if self._should_show_help(argv):
            self._show_help()
            return CliResult([], exit_code=1)

        self._setup_runtime()

        self.backend = self._determine_backend()

        handler_result = self._execute_backend(remaining)
        #print(f"@@@ hander_result = {type(handler_result)}, datatype={type(handler_result.data)}")
        if self.session:
            self.session.result_store.add(handler_result)
        return self._normalize_result([handler_result])


    def compute_exit_code(self, results: Iterable[HandlerResult]):
        for r in results:
            if r.kind == ResultKind.FAILED:
                return 1
        return 0

    def _normalize_argv(self, argv: Iterable[str]|None) -> list[str]:
        if argv is None:
            argv = sys.argv[1:]

        if isinstance(argv, str):
            import shlex
            argv = shlex.split(argv)

        return list(argv)


    def _early_parse(self, argv: Sequence[str]) -> Tuple[argparse.Namespace|None, Sequence[str]]:
        parser = self._build_early_parser()
        if parser:
            return parser.parse_known_args(argv)
        return None, argv


    def _build_early_parser(self) -> argparse.ArgumentParser|None:
        early_parser = self.builder.build_early_argparse(self.cli_def)
        return early_parser


    def _make_context(self, args: argparse.Namespace|None=None):
        return make_runtime_context(args, self.default_ctx)


    def _setup_runtime(self):
        assert self.ctx is not None
        setup_logging(self.ctx)


    def _should_show_help(self, argv: Sequence[str]):
        return "--help" in argv or "-h" in argv


    def show_help(self):
        return self._show_help()


    def _show_help(self):
        dump_cli_def_pretty(self.cli_def, as_help=True)


    def _determine_backend(self) -> str:
        assert self.ctx is not None
        backend = self.ctx.backend or self.default_backend
        return backend or "argparse"


    def _execute_backend(self, argv: Sequence[str]):
        if self.backend == "click":
            logging.info("[click] backend")
            return self._execute_click(argv)

        logging.info("[argparse] backend")
        return self._execute_argparse(argv)


    def _execute_argparse(self, argv: Sequence[str]) -> Any:
        builder = self.builder
        if builder is None:
            builder = ArgparseBuilder()
        parser = builder.build_argparse(self.cli_def)
        args, remaining = parser.parse_known_args(args=argv)
        return self.dispatcher.dispatch(args, remaining, ctx=self.ctx)


    def _execute_click(self, argv: Sequence[str]) -> Any:
        import click
        from ..backend.click import ClickBuilder, ClickBinder
        builder = ClickBuilder()
        root = builder.build_click(self.cli_def)

        binder = ClickBinder(dispatcher=self.dispatcher, ctx=self.ctx)
        binder.bind(root, builder.defpath_mapping)

        try:
            result = root(
                args=list(argv) if argv is not None else None,
                standalone_mode=False,
            )

            return result

        except click.exceptions.NoArgsIsHelpError as e:
            click.echo(e.ctx.get_help())
            return 0

        except click.exceptions.ClickException as e:
            e.show()
            return e.exit_code

    def _normalize_result(self, results: Iterable[HandlerResult]) -> CliResult:
        exit_code = self.compute_exit_code(results)
        result = CliResult(
            exit_code=exit_code,
            results=list(results)
        )
        return result
