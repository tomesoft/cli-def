# cli_def/runtime/utils.py
from __future__ import annotations
from typing import Sequence, Any, Callable, Optional, Tuple

import sys
import argparse
import logging

from ..models import CliDef
from ..backend.argparse import ArgparseBuilder
from .dispatcher import CliDispatcher
from .event import CliEvent
from .context import CliRuntimeContext


def make_runtime_context(
        args: argparse.Namespace|None = None,
        default_ctx: CliRuntimeContext|None = None,
        ) -> CliRuntimeContext:
    if args is None:
        return default_ctx or CliRuntimeContext()

    ctx = CliRuntimeContext(
        debug=bool(getattr(args, "debug", False)),
        verbose=bool(getattr(args, "verbose", False)),
        lang=getattr(args, "lang", "en"),
        backend=getattr(args, "backend", None),
        extra={
            k: v for k, v in vars(args).items()
            if not k.startswith("_") and
                not k in ("debug", "verbose", "lang", "backend")
        }
    )
    return ctx


def setup_logging(ctx: CliRuntimeContext):
    level = logging.DEBUG if ctx.debug else logging.INFO if ctx.verbose else logging.WARNING
    #print(f"level={level}, {logging.getLevelName(level)}")
    #logging.basicConfig(level=level) # does not work
    logger = logging.getLogger()
    logger.setLevel(level)
    if level < logging.WARNING:
        logging.info(f"level={get_logging_level_name()}")


def get_logging_level() -> int:
    logger = logging.getLogger()
    return logger.level


def get_logging_level_name() -> str:
    level = get_logging_level()
    
    for k, v in logging.getLevelNamesMapping().items():
        if v == level:
            return k
    return "UNKNOWN_LEVEL"


# def execute_early_only(
#         cli_def: CliDef,
#         argv: Optional[Sequence[str]] = None,
#         builder: Optional[ArgparseBuilder] = None,
# ) -> Tuple[CliRuntimeContext, Sequence[str]]:

#     if argv is None:
#         argv = sys.argv[1:]
#     if builder is None:
#         builder = ArgparseBuilder()

#     early_parser = builder.build_early_argparse(cli_def)
#     if early_parser:
#         args, remaining = early_parser.parse_known_args(args=argv)
#         ctx = make_runtime_context(args)
#         setup_logging(ctx)
#     else:
#         ctx = make_runtime_context()
#         remaining = argv

#     return (ctx, remaining)


# def execute_cli(
#         cli_def: CliDef,
#         argv: Optional[Sequence[str]] = None,
#         builder: Optional[ArgparseBuilder] = None,
#         fallback_handler: Callable[[CliEvent], Any] = None,
#         ctx: CliRuntimeContext = None,
#         *,
#         early_parsing: bool = False,
#         default_backend: str = None,
#         ) -> Any:

#     if argv is None:
#         argv = sys.argv[1:]

#     if builder is None:
#         builder = ArgparseBuilder()

#     if early_parsing:
#         ctx, remaining = execute_early_only(
#             cli_def,
#             argv=argv,
#             builder=builder,
#         )
#         argv = remaining


#     if ctx is None:
#         ctx = make_runtime_context()

#     if ctx.backend is None:
#         ctx.backend = default_backend or "argparse"

#     print(f"@@@ ctx={ctx}")

#     if ctx.backend == "click":
#         logging.info("[click] backend")
#         result = _execute_cli_click(
#             cli_def,
#             builder=builder,
#             argv=argv,
#             fallback_handler=fallback_handler,
#             ctx=ctx,
#             )
#     else:
#         logging.info("[argparse] backend")
#         result = _execute_cli_argparse(
#             cli_def,
#             builder=builder,
#             argv=argv,
#             fallback_handler=fallback_handler,
#             ctx=ctx,
#             )

#     return result


# def _execute_cli_argparse(
#         cli_def: CliDef,
#         argv: Optional[Sequence[str]] = None,
#         builder: Optional[Any] = None,
#         fallback_handler: Callable[[CliEvent], Any] = None,
#         ctx: CliRuntimeContext = None,
#         ) -> Any:
#     if builder is None:
#         builder = ArgparseBuilder()
#     parser = builder.build_argparse(cli_def)
#     dispatcher = Dispatcher(
#         cli_def,
#         fallback_handler=fallback_handler
#     )
#     args, remaining = parser.parse_known_args(args=argv)
#     return dispatcher.dispatch(args, remaining)


# def _execute_cli_click(
#         cli_def: CliDef,
#         argv: Optional[Sequence[str]] = None,
#         builder: Optional[Any] = None,
#         fallback_handler: Callable[[CliEvent], Any] = None,
#         ctx: CliRuntimeContext = None,
#     ) -> Any:
#     import click
#     from ..click import ClickBuilder, ClickBinder
#     builder2 = ClickBuilder()
#     root = builder2.build_click(cli_def)

#     dispatcher = Dispatcher(
#         cli_def,
#         fallback_handler=fallback_handler
#     )
#     binder = ClickBinder(dispatcher=dispatcher)
#     binder.bind(root, builder2.defpath_mapping)

#     try:
#         return root(
#             args=list(argv) if argv is not None else None,
#             standalone_mode=False,
#         )

#     except click.exceptions.NoArgsIsHelpError as e:
#         click.echo(e.ctx.get_help())
#         return 0

#     except click.exceptions.ClickException as e:
#         e.show()
#         return e.exit_code