# cli_def/parsers/parser.py

from typing import Mapping, Any, Iterable
import tomllib
from pathlib import Path
import importlib
import logging

from ..models import (
    CliDef,
    CommandDef,
    ArgumentDef,
    MultDef,
)

# --------------------------------------------------------------------------------
# CliDefParser class
# --------------------------------------------------------------------------------
class CliDefParser:

    def parse_from_toml(self, path_to_toml_file: str) -> CliDef | None:
        mapping = {}
        with open(path_to_toml_file, "rb") as file:
            mapping = tomllib.load(file)
        if "cli" in mapping:
            return self.parse_from_mapping(mapping)
        return None


    def parse_from_toml_text(self, toml_text: str) -> CliDef | None:
        mapping = {}
        mapping.update(tomllib.loads(toml_text))
        if "cli" in mapping:
            return self.parse_from_mapping(mapping)
        return None


    def parse_from_mapping(self, mapping: Mapping[str, Any]) -> CliDef | None:
        cliDef = CliDef()
        argDefs = []
        commandDefs = []
        for key, value in mapping.get("cli", {}).items():
            if key == "args":
                argDefs = self.parse_cli_argument_defs(key, value)
            elif hasattr(cliDef, key):
                setattr(cliDef, key, value)
            elif isinstance(value, Mapping):
                commandDef = self.parse_cli_command_def(key, value)
                if commandDef:
                    commandDefs.append(commandDef)
            else:
                cliDef.extra_defs[key] = value

        for argDef in argDefs:
            argDef.parent = cliDef
        cliDef.arguments = argDefs
        for cmdDef in commandDefs:
            cmdDef.parent = cliDef
        cliDef.commands = commandDefs
        return cliDef


    def parse_cli_argument_defs(self, key: str, mappings: Iterable[Mapping[str, Any]]) -> Iterable[ArgumentDef] | None:
        argDefs = []
        for mapping in mappings:
            argDef = ArgumentDef.from_mapping(mapping)
            if argDef.key:
                argDefs.append(argDef)
            else:
                logging.warning(f"key not found {argDefs}")
        return argDefs


    def parse_cli_command_def(self, key: str, mapping: Mapping[str, Any]) -> CommandDef | None:
        commandDef = CommandDef(
            key=key,
            is_template=key.startswith("_"), # special rule
            )
        for key, value in mapping.items():
            argDefs = []
            if key == "args":
                argDefs = self.parse_cli_argument_defs(key, value)
                if argDefs:
                    for argDef in argDefs:
                        argDef.parent = commandDef
                    commandDef.arguments = argDefs
            elif hasattr(commandDef, key):
                setattr(commandDef, key, value)
            elif isinstance(value, Mapping):
                # parse as subcommands
                if commandDef.subcommands is None:
                    commandDef.subcommands = []
                subcommandDef = self.parse_cli_command_def(key, value)
                subcommandDef.parent = commandDef
                commandDef.subcommands.append(subcommandDef)
            else:
                commandDef.extra_defs[key] = value
            
        return commandDef

