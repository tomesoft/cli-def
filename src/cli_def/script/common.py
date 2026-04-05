# cli_def/script/handlers/common.py
from __future__ import annotations

from importlib import resources

from ..runtime import (
    CliEvent,
)
from ..ops import (
    load_cli_def_path,
)


def load_builtin_cli_def(*relative_paths):
    path = resources.files("cli_def.resources")
    if len(relative_paths):
        path = path.joinpath(*relative_paths)
    else:
        path = path.joinpath("cli_def.toml")
    return load_cli_def_path(path)


def print_handler(event: CliEvent):
    print("=== fallback handler ===")
    print("  PATH:", event.path)
    print("  PARAMS:", event.params)
    if event.extra_args:
        print("  EXTRA:", event.extra_args)

