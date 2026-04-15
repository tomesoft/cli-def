# cli_def/script/main.py
from __future__ import annotations
from typing import Sequence
import logging
import sys

from ..runtime import CliRunner

from .common import (
    load_builtin_cli_def,
    print_handler
)


# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------

def main(argv: Sequence[str]|None=None):
    if argv is None:
        argv = sys.argv[1:]

    cli_def = load_builtin_cli_def()
    assert cli_def is not None
    runner = CliRunner(
        cli_def,
        handle_early_parse=True,
        fallback_handler=print_handler
    )

    result = runner.run(argv)

    logging.info(f"@@@ cli_def.sctipt.main:result = {result}")

    return result.exit_code

