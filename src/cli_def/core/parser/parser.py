# cli_def/core/parser/parser.py
from __future__ import annotations

from typing import Mapping, Any, Iterable
import tomllib
from pathlib import Path
import logging

from ..models import (
    CliDef,
    CommandDef,
    ArgumentDef,
    MultDef,
)

from ...basic.basic_types import PathLike

# --------------------------------------------------------------------------------
# CliDefParser class
# --------------------------------------------------------------------------------
class CliDefParser:

    def parse_from_toml(self, path_to_toml_file: PathLike) -> CliDef | None:
        mapping = {}
        with open(path_to_toml_file, "rb") as file:
            mapping = tomllib.load(file)
        if "cli" in mapping:
            cli_def = self.parse_from_mapping(mapping)
            if cli_def is not None:
                cli_def.set_source(path_to_toml_file)
            return cli_def
        return None


    def parse_from_tomls(self, path_to_toml_files: Iterable[PathLike]) -> CliDef | None:
        merged_items = {}
        for file in path_to_toml_files:
            with open(file, "rb") as file:
                mapping = tomllib.load(file)
            if "cli" in mapping:
                merged_items.update(
                    {k:v for k, v in mapping["cli"].items()}
                )
                # print(f"@@@@ merged: {merged_items}")
        if merged_items:
            mapping = {"cli": merged_items}
            cli_def = self.parse_from_mapping(mapping)
            return cli_def
        return None


    def parse_from_toml_text(self, toml_text: str) -> CliDef | None:
        mapping = {}
        mapping.update(tomllib.loads(toml_text))
        if "cli" in mapping:
            return self.parse_from_mapping(mapping)
        return None


    def parse_from_mapping(self, mapping: Mapping[str, Any]) -> CliDef | None:

        cli_def_mapping = mapping.get("cli", {})
        if len(cli_def_mapping) == 0:
            return None

        known, remaining = CliDef.split_mapping(cli_def_mapping)
        # 1) apply known fields
        cliDef = CliDef(**known)

        # 2) apply remainings
        argDefs:Iterable[ArgumentDef] = []
        commandDefs:Iterable[CommandDef] = []
        for key, value in remaining.items():
            if key == "args":
                argDefs = self.parse_cli_argument_defs(key, value)
            elif isinstance(value, Mapping):
                commandDef = self.parse_cli_command_def(key, value)
                if commandDef:
                    commandDefs.append(commandDef)
            else:
                cliDef._extra_defs[key] = value

        assert cliDef.key is not None

        for argDef in argDefs:
            argDef._parent = cliDef
        cliDef._arguments = list(argDefs)
        for cmdDef in commandDefs:
            cmdDef._parent = cliDef
        cliDef._commands = commandDefs
        return cliDef


    def parse_cli_argument_defs(self, key: str, mappings: Iterable[Mapping[str, Any]]) -> Iterable[ArgumentDef]:
        argDefs = []
        for mapping in mappings:
            known, remaining = ArgumentDef.split_mapping(mapping)
            argDef = ArgumentDef(**known)
            if remaining:
                argDef._extra_defs.update(remaining)
            argDefs.append(argDef)
            # argDef = ArgumentDef.from_mapping(mapping)
            # if argDef.key:
            #     argDefs.append(argDef)
            # else:
            #     logging.warning(f"key not found {argDefs}")
        return argDefs


    def parse_cli_command_def(self, key: str, mapping: Mapping[str, Any]) -> CommandDef:

        known, remaining = CommandDef.split_mapping(mapping)

        # 1) apply known fields
        commandDef = CommandDef(key, **known)

        # 2) apply remainings
        for key, value in remaining.items():
            argDefs = []
            if key == "args":
                argDefs = self.parse_cli_argument_defs(key, value)
                if argDefs:
                    for argDef in argDefs:
                        argDef._parent = commandDef
                    commandDef._arguments = list(argDefs)
            elif isinstance(value, Mapping):
                # parse as subcommands
                if commandDef._subcommands is None:
                    commandDef._subcommands = []
                subcommandDef = self.parse_cli_command_def(key, value)
                subcommandDef._parent = commandDef
                commandDef._subcommands.append(subcommandDef)
            else:
                commandDef._extra_defs[key] = value
            
        return commandDef

