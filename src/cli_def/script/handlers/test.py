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
from ...test_support.test_generator import CliTestGenerator

# --------------------------------------------------------------------------------
#
# test run command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/test/run", description="builtin run test command handler", late_binding=True)
def run_test(event: CliEvent):

    cli_test_file = event.params.get("cli_test_file")
    assert cli_test_file

    logging.info("=== run test command ===")

    test_runner = CliTestRunner()
    test_runner.run(cli_test_file)


# --------------------------------------------------------------------------------
#
# test generate command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/test/generate", description="builtin generate test command handler", late_binding=True)
def generate_test(event: CliEvent):

    cli_def_file = event.params.get("cli_def_file")
    with_output = event.params.get("with_output") or False
    assert cli_def_file

    logging.info("=== test command ===")

    test_generator = CliTestGenerator()
    result = test_generator.generate_from(cli_def_file, with_output=with_output)

    if result is None:
        msg = f"Could not load cli-def from: {cli_def_file}"
        return CliHandlerResult.make_error(event, msg)

    for l in result:
        print(l)

    return CliHandlerResult.make_result(event, data=result)

