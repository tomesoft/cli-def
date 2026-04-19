# cli_def/ops/loader.py
from __future__ import annotations

from typing import Mapping, Any, Union
from pathlib import Path
import logging
import tomllib

from typing import Union
from pathlib import Path

PathLike = Union[str, Path]

from ..core.models.raw import CliDef
from ..core.parser import CliDefParser


def load_toml_beside(
        here: Path,
        *path_parts: PathLike
    ) -> Mapping[str, Any]:
    """
    Usage:
        load_toml_beside(Path(__file__), "cli_def.toml")
        load_toml_beside(Path(__file__), "resources", "cli_def.toml")
    """
    base = here.resolve().parent
    toml_path = base.joinpath(*path_parts)
    with toml_path.open("rb") as f:
        return tomllib.load(f)


def load_cli_def_beside(
        here: Path,
        *path_parts: PathLike
    ) -> CliDef | None:
    """
    Usage:
        load_cli_def_beside(Path(__file__), "cli_def.toml")
        load_cli_def_beside(Path(__file__), "profiles", f"{profile}.toml")
    """
    base = here.resolve().parent
    toml_path = base.joinpath(*path_parts)
    return load_cli_def_path(toml_path)


def load_cli_def_path(path_to_toml: PathLike) -> CliDef | None:
    if path_to_toml is None:
        return None
    if not Path(path_to_toml).exists():
        logging.warning(f"cli_def file not found: {path_to_toml}")
        return None

    parser = CliDefParser()
    cli_def = parser.parse_from_toml(path_to_toml)
    return cli_def
