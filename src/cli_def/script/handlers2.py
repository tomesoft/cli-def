# cli_def/script/handlers.py
from typing import Sequence, Any

from importlib import resources

from ..runtime import (
    cli_def_handler,
    CliEvent,
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