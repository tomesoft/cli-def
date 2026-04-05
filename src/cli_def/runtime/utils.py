# cli_def/runtime/utils.py
from __future__ import annotations
from typing import Sequence, Any

import argparse
import logging

from .context import CliRuntimeContext


def make_runtime_context(
        args: argparse.Namespace|None = None,
        default_ctx: CliRuntimeContext|None = None,
    ) -> CliRuntimeContext:
    if args is None:
        return default_ctx or CliRuntimeContext()

    ctx = CliRuntimeContext(
        debug=bool(getattr(args, "debug", False)),
        verbose=bool(getattr(args, "verbose", False)),
        lang=getattr(args, "lang", "en"),
        backend=getattr(args, "backend", None),
        extra={
            k: v for k, v in vars(args).items()
            if not k.startswith("_") and
                not k in ("debug", "verbose", "lang", "backend")
        }
    )
    return ctx


def setup_logging(ctx: CliRuntimeContext):
    level = logging.DEBUG if ctx.debug else logging.INFO if ctx.verbose else logging.WARNING
    #print(f"level={level}, {logging.getLevelName(level)}")
    #logging.basicConfig(level=level) # does not work
    logger = logging.getLogger()
    logger.setLevel(level)
    if level < logging.WARNING:
        logging.info(f"level={get_logging_level_name()}")


def get_logging_level() -> int:
    logger = logging.getLogger()
    return logger.level


def get_logging_level_name() -> str:
    level = get_logging_level()
    
    for k, v in logging.getLevelNamesMapping().items():
        if v == level:
            return k
    return "UNKNOWN_LEVEL"

