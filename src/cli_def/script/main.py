# cli_def/script/main.py
from typing import Sequence
import argparse
import logging
import sys

from importlib import resources

from ..parsers import CliDefParser
from ..models import CliDef
from ..argparse import ArgparseBuilder
from ..runtime import (
    CliEvent,
    Dispatcher,
    CliSession,
)
from ..runtime import cli_def_handler
from ..runtime.utils import (
    execute_cli,
    get_logging_level,
    setup_logging,
    make_runtime_context,
)


import cli_def.script.handlers
from .handlers import (
    load_builtin_cli_def,
    dump_cli_def,
    print_handler
)

# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------

def main(argv: Sequence[str]=None):
    if argv is None:
        argv = sys.argv[1:]

    cli_def = load_builtin_cli_def()
    builder = ArgparseBuilder()
    early_parser = builder.build_early_argparse(cli_def)

    if early_parser:
        args, remaining = early_parser.parse_known_args(argv)
        ctx = make_runtime_context(args)
        setup_logging(ctx)
    else:
        remaining = argv
        logging.debug(f"remaining:{remaining}")

    if get_logging_level() <= logging.INFO:
        dump_cli_def(cli_def)

    execute_cli(cli_def, builder=builder, argv=remaining, fallback_handler=print_handler)



