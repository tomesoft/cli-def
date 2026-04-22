# cli_def/script/handlers/test.py
from __future__ import annotations
from typing import Sequence, Any
import logging
from pathlib import Path

from ...basic.basic_types import PathLike

from ...runtime import (
    CliEvent,
    CliHandlerResult,
    cli_def_handler
)
from ...ops import (
    load_cli_def_path,
    CliDefDumper,
)
from ...ops.utils.renderer import Table

from ...test_support.test_runner import CliTestRunner


# --------------------------------------------------------------------------------
#
# test command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/test", description="builtin test command handler", late_binding=True)
def run_test(event: CliEvent):

    cli_test_file = event.params.get("cli_test_file")
    assert cli_test_file

    logging.info("=== test command ===")

    test_runner = CliTestRunner()
    test_runner.run(cli_test_file)
