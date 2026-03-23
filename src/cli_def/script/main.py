# cli_def/script/main.py
import argparse

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

def main():
    cli_def = load_builtin_cli_def()

    dump_cli_def(cli_def)

    execute_cli(cli_def, fallback_handler=print_handler)

if __name__ == "__main__":
    main()


