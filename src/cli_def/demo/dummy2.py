# cli_def/demo/dummy2.py

from ..runtime import (
    cli_def_handler,
    CliEvent,
)


# --------------------------------------------------------------------------------
# dummy handlers for scan command
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/testA", late_binding=True, description="late binding testA")
def dummyA(event: CliEvent):
    pass

@cli_def_handler("/cli-def/testB", late_binding=True, description="late binding testB", tags=["demo"])
def dummyB(event: CliEvent):
    pass

@cli_def_handler("/cli-def/testC", late_binding=True, description="late binding testC", tags=["demo"])
def dummyC(event: CliEvent):
    pass