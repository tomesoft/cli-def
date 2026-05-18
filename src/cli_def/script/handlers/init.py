# cli_def/script/handlers/init.py
from __future__ import annotations
from typing import Sequence, Any
import logging
from pathlib import Path
from shutil import copytree

from ...basic.basic_types import PathLike

from ...runtime import (
    CliEvent,
    CliHandlerResult,
)

from ...runtime import cli_def_handler, CliHandlerResult

from importlib.resources import files


# --------------------------------------------------------------------------------
#
# dump command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/init", description="builtin init command handler", late_binding=True)
def run_init(event: CliEvent):

    new_project = event.params.get("new_project")
    assert new_project is not None

    path = Path(new_project)

    if path.exists():
        msg = f"Error {path} already exists"
        print(msg)
        return CliHandlerResult.make_error(event, msg)

    template_dir = files("cli_def.resources.templates").joinpath("basic")
    copytree(str(template_dir), new_project)

    print(f"Project created: {new_project}")

    return CliHandlerResult.make_result(
        event,
        "run_init",
        data=None
    )

