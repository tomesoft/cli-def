# cli_def/runtime/runner.py
from __future__ import annotations
from typing import Sequence, Iterable, Any, Callable, TYPE_CHECKING, Tuple

import io
from contextlib import redirect_stdout, redirect_stderr
import sys
import argparse
import logging

from ..core.models import (
    CliDef,
    ResolvedCliDef,
)
from ..backend.argparse import ArgparseBuilder
from ..ops import CliDefDumper
from ..core.resolver import CliDefResolver


from .dispatcher import CliDispatcher
from .context import CliRuntimeContext
from .event import CliEvent
from .result import (
    CliHandlerResult,
    CliHandlerResultKind,
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
            fallback_handler: Callable[[CliEvent], CliHandlerResult|None]|None = None,
            *,
            default_backend: str="argparse",
            default_ctx: CliRuntimeContext|None = None,
            session: CliSession|None = None,
            handle_early_parse: bool = False,
            dry_run_handler: Callable[[CliEvent], CliHandlerResult|None]|None = None,
            ):
        self.cli_def = cli_def
        self.fallback_handler = fallback_handler
        self.default_backend = default_backend
        self.backend: str|None = None
        self.default_ctx = default_ctx
        self.session = session
        self._handle_early_parse: bool = handle_early_parse

        self.cli_def_resolved: ResolvedCliDef = CliDefResolver().resolve(self.cli_def)
        self.ctx: CliRuntimeContext|None = None
        self.builder: ArgparseBuilder = ArgparseBuilder()
        self.dispatcher: CliDispatcher = CliDispatcher(
            self.cli_def_resolved,
            fallback_handler=self.fallback_handler,
            dry_run_handler=dry_run_handler,
        )


    def run(self, argv: Iterable[str]| str | None = None) -> CliResult:
        #print("@@@1")
        argv = self._normalize_argv(argv)
        #print("@@@2")

        if self._handle_early_parse:
            early_args, remaining = self._early_parse(argv)
            logging.debug(f"@@@@ early_args:{early_args}, remaining:{remaining}")

            self.ctx = self._make_context(early_args)
        else:
            remaining = argv
            self.ctx = self._make_context()

        #print("@@@3")
        # if self._should_show_help(argv):
        #     self._show_help()
        #     return CliResult([], exit_code=1)

        #print("@@@4")
        self._setup_runtime()

        #print("@@@5")
        self.backend = self._determine_backend()

        #print("@@@6")
        handler_result = self._execute_backend(remaining)
        #print(f"@@@ hander_result type = {type(handler_result)}")
        #print("@@@7")
        if self.session:
            self.session.result_store.add(handler_result)
        #print("@@@8")
        return self._normalize_result([handler_result])


    def run_and_capture(self, argv: Iterable[str] | str | None = None) -> Tuple[CliResult, str, str]:
        out = io.StringIO()
        err = io.StringIO()

        try:
            with redirect_stdout(out), redirect_stderr(err):
                result = self.run(argv)
        except Exception as e:
            return CliResult([], exit_code=1), out.getvalue(), err.getvalue()

        return result, out.getvalue(), err.getvalue()


    def compute_exit_code(self, results: Iterable[CliHandlerResult]):
        results = list(results)
        if len(results) == 1 and isinstance(results[0], int):
            # click returns 2 when parser error happened
            return results[0]
        for r in results:
            if r.kind == CliHandlerResultKind.FAILED:
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
        #print(f"@@@@ _early_parser = {parser}")
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


    def show_help(self, use_backend: bool = False):
        return self._show_help()


    def _show_help(self):
        CliDefDumper.dump_pretty(self.cli_def_resolved, as_help=True, as_resolved=True)


    def _determine_backend(self) -> str:
        assert self.ctx is not None
        backend = self.ctx.backend or self.default_backend
        return backend or "argparse"


    def _execute_backend(self, argv: Sequence[str]) -> Any:
        if self.backend == "click":
            logging.info(f"[click] backend argv:{argv!r}")
            return self._execute_click(argv)

        logging.info(f"[argparse] backend argv:{argv!r}")
        return self._execute_argparse(argv)


    def _execute_argparse(self, argv: Sequence[str]) -> Any:
        builder = self.builder
        if builder is None:
            builder = ArgparseBuilder()
        parser = builder.build(self.cli_def_resolved)
        args, remaining = parser.parse_known_args(args=argv)
        return self.dispatcher.dispatch(args, remaining, ctx=self.ctx)


    def _execute_click(self, argv: Sequence[str]) -> Any:
        import click
        from ..backend.click import ClickBuilder, ClickBinder
        builder = ClickBuilder()
        root = builder.build(self.cli_def_resolved)

        binder = ClickBinder(dispatcher=self.dispatcher, ctx=self.ctx)
        binder.bind(builder.defpath_mapping)

        try:
            args=list(argv) if argv is not None else None
            #print(f"@@@ argv = {args!r}")
            result = root(
                args=args,
                standalone_mode=False,
            )

            return result

        except click.exceptions.NoArgsIsHelpError as e:
            click.echo(e.ctx.get_help())
            return 0

        except click.exceptions.ClickException as e:
            e.show()
            #print(f"@@@ click.exception {e.exit_code}")
            return e.exit_code

    def _normalize_result(self, results: Iterable[CliHandlerResult]) -> CliResult:
        exit_code = self.compute_exit_code(results)
        result = CliResult(
            exit_code=exit_code,
            results=list(results) if exit_code < 2 else []
        )
        return result
