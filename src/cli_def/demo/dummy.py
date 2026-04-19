# cli_def/demo/dummy.py
from __future__ import annotations
from typing import Sequence, Any
import logging
import copy
from pathlib import Path

from ..runtime import (
    CliEvent,
)

from ..runtime import cli_def_handler, CliHandlerResult





# --------------------------------------------------------------------------------
# dummy handlers for scan command test
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/test1", late_binding=False, description="early binding test1")
def dummy1_early(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test2", late_binding=False, description="early binding test2", tags=["demo"])
def dummy2_early(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test3", late_binding=False, description="learly binding test3", tags=["demo"])
def dummy3_early(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test1", late_binding=True, description="late binding test1")
def dummy1(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test2", late_binding=True, description="late binding test2", tags=["demo"])
def dummy2(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test3", late_binding=True, description="late binding test3", tags=["demo"])
def dummy3(event: CliEvent):
    pass