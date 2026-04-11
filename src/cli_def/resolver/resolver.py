# cli_def/resolver/resolver.py
from __future__ import annotations
from typing import Mapping, Any, Sequence
import logging

from ..models import (
    CliDefNode,
    ExecutableNode,
    CliDef,
    CommandDef,
    ArgumentDef,
)

class CliDefResolver:

    def __init__(self):
        self.defpath_mapping: dict[str, CliDefNode]|None = None


    def resolve(self, cli_def: CliDef) -> CliDef:
        self.defpath_mapping = {
            node.defpath: node
            for node in cli_def.iter_all_nodes()
        }
        
        new_cliDef = CliDef(key=cli_def.key)
        new_cliDef.source = cli_def
        new_cliDef.override_with(cli_def)
        for node in cli_def.iter_children():
            if isinstance(node, CommandDef):
                new_cmdDef = self.resolve_commandDef(node)
                if new_cmdDef:
                    if new_cliDef.commands is None:
                        new_cliDef.commands = []
                    new_cliDef.commands.append(new_cmdDef)
                    new_cmdDef.parent = new_cliDef
            elif isinstance(node, ArgumentDef):
                new_argDef = self.resolve_argumentDef(node)
                if new_argDef:
                    new_cliDef.arguments.append(new_argDef)
                    new_argDef.parent = new_cliDef

        # parameter binding
        self.bind_parameters(new_cliDef)

        new_cliDef.resolved = True

        return new_cliDef


    def resolve_commandDef(self, cmdDef: CommandDef) -> CommandDef|None:
        if cmdDef.is_template:
            return None

        new_cmdDef = CommandDef(cmdDef.key)
        new_cmdDef.source = cmdDef

        new_arg_def_mapping: dict[str, ArgumentDef] = {}

        # 1) apply from predecessors
        for predecessor in self.get_predecessors(cmdDef):
            new_cmdDef.override_with(predecessor)

            for arg in predecessor.arguments:
                new_argDef = self.resolve_argumentDef(arg)
                if new_argDef:
                    new_arg_def_mapping[new_argDef.key] = new_argDef

        # 2) apply from children
        for node in cmdDef.iter_children():
            if isinstance(node, CommandDef):
                new_subCmdDef = self.resolve_commandDef(node)
                if new_subCmdDef:
                    if new_cmdDef.subcommands is None:
                        new_cmdDef.subcommands = []
                    new_cmdDef.subcommands.append(new_subCmdDef)
                    new_subCmdDef.parent = new_cmdDef
            elif isinstance(node, ArgumentDef):
                new_argDef = self.resolve_argumentDef(node)
                if new_argDef:
                    new_arg_def_mapping[new_argDef.key] = new_argDef

        # 3) fix members
        new_cmdDef.override_with(cmdDef)
        for k, v in new_arg_def_mapping.items():
            new_cmdDef.arguments.append(v)
            v.parent = new_cmdDef

        # 4) parameter binding
        self.bind_parameters(new_cmdDef)

        return new_cmdDef


    def resolve_argumentDef(self, argDef: ArgumentDef) -> ArgumentDef:
        new_argDef = ArgumentDef(argDef.key)
        new_argDef.source = argDef
        new_argDef.override_with(argDef)

        return new_argDef


    def resolve_predecessor(self, cmdDef: CommandDef, keyOrPath: str) -> CommandDef|None:
        if keyOrPath.startswith("/") and self.defpath_mapping: # means path specified
            node = self.defpath_mapping.get(keyOrPath, None)
            if node is None:
                return None
            if isinstance(node, CommandDef):
                assert node != cmdDef
                assert node.key != cmdDef.key
                return node
            return None
        else:
            if cmdDef.parent:
                for node in cmdDef.parent.iter_children():
                    if node == cmdDef:
                        continue # reject itself
                    if node.key == cmdDef.key:
                        continue # reject of same key
                    if isinstance(node, CommandDef) and node.key == keyOrPath:
                        return node
        return None


    def get_predecessors(self, cmdDef: CommandDef) -> Sequence[CommandDef]:
        predecessors: list[CommandDef] = []
        if cmdDef.inherit_from:
            for keyOrPath in cmdDef.inherit_from:
                item = self.resolve_predecessor(cmdDef, keyOrPath)
                if item is not None and item.subcommands is None: # reject group
                    predecessors.append(item)
                else:
                    logging.warning(f"Could not resolve predecessor entry `{keyOrPath}` in inherit_from of CommandDef({cmdDef.defpath})")
        else: # fully inherit from templates
            predecessors.extend(cmdDef.get_templates())
        return predecessors


    def bind_parameters(self, executable: ExecutableNode):
        if executable.bind is not None:
            bind_mapping: dict[str, Any] = dict(executable.bind)
            if isinstance(executable, CliDef|CommandDef):
                for argDef in executable.arguments:
                    if argDef.key in bind_mapping:
                        argDef.bound = bind_mapping.pop(argDef.key)
            # re-assign remaingings 
            executable.bind = bind_mapping
