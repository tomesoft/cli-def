# cli_def/runtime/utils.py
from typing import Sequence, Any, Callable, Optional

import argparse

from ..models import CliDef
from ..argparse import ArgparseBuilder
from .dispatcher import Dispatcher
from .event import CliEvent

def build_parser(cli_def: CliDef) -> argparse.ArgumentParser:
    builder = ArgparseBuilder()
    return builder.build_argparse(cli_def)

def execute_cli(
        cli_def: CliDef,
        argv: Optional[Sequence[str]] = None,
        fallback_handler: Callable[[CliEvent], Any] = None,
        ) -> Any:
    parser = build_parser(cli_def)
    dispatcher = Dispatcher(cli_def,fallback_handler=fallback_handler)
    args, remaining = parser.parse_known_args(args=argv)
    return dispatcher.dispatch(args, remaining)