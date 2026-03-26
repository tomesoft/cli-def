# cli_def/runtime/utils.py
from typing import Sequence, Any, Callable, Optional

import argparse
import logging

from ..models import CliDef
from ..argparse import ArgparseBuilder
from .dispatcher import Dispatcher
from .event import CliEvent
from .context import CliRuntimeContext


def make_runtime_context(args: argparse.Namespace) -> CliRuntimeContext:
    ctx = CliRuntimeContext(
        debug=bool(getattr(args, "debug", False)),
        verbose=bool(getattr(args, "verbose", False)),
        lang=bool(getattr(args, "lang", "en")),
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



def execute_cli(
        cli_def: CliDef,
        argv: Optional[Sequence[str]] = None,
        builder: Optional[ArgparseBuilder] = None,
        fallback_handler: Callable[[CliEvent], Any] = None,
        *,
        early_parse: bool = False,
        ) -> Any:
    if builder is None:
        builder = ArgparseBuilder()
    # if early_parse:
    #     early_parser = builder.build_early_argparse(cli_def)
    #     ctx = make_runtime_context()
    parser = builder.build_argparse(cli_def)
    dispatcher = Dispatcher(cli_def,fallback_handler=fallback_handler)
    args, remaining = parser.parse_known_args(args=argv)
    return dispatcher.dispatch(args, remaining)


