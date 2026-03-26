# cli_def/script/handlers.py
from typing import Sequence, Any
import argparse
import logging

from importlib import resources

from ..models import CliDef
from ..parsers import CliDefParser
from ..argparse import ArgparseBuilder
from ..runtime import (
    CliEvent,
    Dispatcher,
    CliSession,
)
from ..ops import (
    load_cli_def_path,
    dump_cli_def_pretty,
)
from ..runtime import cli_def_handler
from ..runtime.utils import (
    execute_cli,
)
from ..runtime.handlers import (
    scan_handlers,
)



@cli_def_handler("/cli-def/testA", late_bindings=True, description="late binding testA")
def dummyA(event: CliEvent):
    pass

@cli_def_handler("/cli-def/testB", late_bindings=True, description="late binding testB", tags=["demo"])
def dummyB(event: CliEvent):
    pass

@cli_def_handler("/cli-def/testC", late_bindings=True, description="late binding testC", tags=["demo"])
def dummyC(event: CliEvent):
    pass