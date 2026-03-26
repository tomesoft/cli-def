# cli_def/ops/loader.py

from typing import Mapping, Any
from pathlib import Path
import logging
import tomllib

from ..models import CliDef
from ..parsers import CliDefParser


def load_toml_beside(here: Path, toml_file: str) -> Mapping[str, Any]:
    """
    Typical usage: load_toml_beside(Path(__file__), "cli_def.toml")
    """
    toml_path = here.resolve().parent / toml_file
    with toml_path.open("rb") as f:
        return tomllib.load(f)


def load_cli_def_beside(here: Path, toml_file: str) -> CliDef:
    """
    Typical usage: load_cli_def_beside(Path(__file__), "cli_def.toml")
    """
    toml_path = here.resolve().parent / toml_file
    return load_cli_def_path(toml_path)


def load_cli_def_path(path_to_toml: str) -> CliDef:
    if path_to_toml is None:
        return None
    if not Path(path_to_toml).exists():
        logging.warning(f"cli_def file not found: {path_to_toml}")
        return None

    parser = CliDefParser()
    cli_def = parser.parse_from_toml(path_to_toml)
    return cli_def