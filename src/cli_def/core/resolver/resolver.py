# cli_def/resolver/resolver.py
from __future__ import annotations
from typing import Mapping, Any, Sequence
import logging

from ..models.raw import (
    CliDefNode,
    ExecutableNode,
    CliDef,
    CommandDef,
    ArgumentDef,
)

from ..models.resolved import (
    ResolvedCliDefNode,
    ResolvedExecutableNode,
    ResolvedCliDef,
    ResolvedCommandDef,
    ResolvedArgumentDef,
)

from ..parser import CliDefParser

class CliDefResolver:

    def __init__(self):
        self.defpath_mapping: dict[str, CliDefNode]|None = None

    def resolve_include(self, cli_def: CliDef) -> CliDef:

        if not cli_def.include:
            return cli_def
        
        if not cli_def.source:
            logging.warning("Could not resolve includes due to no source specified.")
            return cli_def

        basepath = cli_def.source.parent
        print(f"@@@@ include base path = {basepath}")
        paths = []
        for file in cli_def.include:
            path = basepath / file
            print(f"@@@@ include path = {path}")
            if path == cli_def.source:
                continue
            paths.append(path)

        paths.append(cli_def.source)
        parser = CliDefParser()
        cli_def_merged = parser.parse_from_tomls(paths)
        if cli_def_merged is None:
            logging.warning("Could not merge includes")
        return cli_def_merged or cli_def



    def resolve(self, cli_def: CliDef) -> ResolvedCliDef:

        tmp_cliDef = CliDef(key=cli_def.key)
        cli_def_base = cli_def

        # 1) resolve_include
        cli_def = self.resolve_include(cli_def_base)


        self.defpath_mapping = {
            node.defpath: node
            for node in cli_def.iter_all_nodes()
        }

        resolved_commands: list[ResolvedCommandDef] = []
        resolved_args: list[ResolvedArgumentDef] = []
        
        tmp_cliDef.override_with(cli_def)
        for node in cli_def.iter_children():
            if isinstance(node, CommandDef):
                resolved_cmdDef = self.resolve_commandDef(node)
                if resolved_cmdDef:
                    resolved_commands.append(resolved_cmdDef)
            elif isinstance(node, ArgumentDef):
                resolved_argDef = self.resolve_argumentDef(node)
                if resolved_argDef:
                    resolved_args.append(resolved_argDef)

        # # parameter binding
        # self.bind_parameters(tmp_cliDef, resolved_args)

        resolved_cliDef = ResolvedCliDef(
            key=cli_def.key,
            definition=cli_def,
            commands=resolved_commands,
            arguments=resolved_args,
            entrypoint=tmp_cliDef.entrypoint,
            extra_defs=tmp_cliDef.extra_defs,
            help=tmp_cliDef.help,
            bound_params=tmp_cliDef.bind,
            group=tmp_cliDef.group,
            prompt=tmp_cliDef.prompt,
        )

        return resolved_cliDef


    def resolve_commandDef(self, cmdDef: CommandDef) -> ResolvedCommandDef|None:
        if cmdDef.is_template:
            return None


        tmp_cmdDef = CommandDef(cmdDef.key)

        new_arg_def_mapping: dict[str, ResolvedArgumentDef] = {}

        # 1) apply from predecessors
        for predecessor in self.get_predecessors(cmdDef):
            tmp_cmdDef.override_with(predecessor)

            for arg in predecessor.arguments:
                resolved_argDef = self.resolve_argumentDef(arg)
                if resolved_argDef:
                    new_arg_def_mapping[resolved_argDef.key] = resolved_argDef

        resolved_subcommands: list[ResolvedCommandDef] = []
        # 2) apply from children
        for node in cmdDef.iter_children():
            if isinstance(node, CommandDef):
                resolved_subCmdDef = self.resolve_commandDef(node)
                if resolved_subCmdDef:
                    resolved_subcommands.append(resolved_subCmdDef)
            elif isinstance(node, ArgumentDef):
                resolved_argDef = self.resolve_argumentDef(node)
                if resolved_argDef:
                    new_arg_def_mapping[resolved_argDef.key] = resolved_argDef

        # 3) parameter binding
        # self.bind_parameters(tmp_cmdDef)

        tmp_cmdDef.override_with(cmdDef)

        # print(f"cmdDef.key:{cmdDef.key}, cmdDef.help:{cmdDef.help}")
        # print(f"tmp_cmdDef.key:{tmp_cmdDef.key}, tmp_cmdDef.help:{tmp_cmdDef.help}")

        # 4) pack into resolved
        resolved_cmdDef = ResolvedCommandDef(
            key=cmdDef.key,
            definition=cmdDef,
            help=tmp_cmdDef.help,
            entrypoint=tmp_cmdDef.entrypoint,
            group=tmp_cmdDef.group,
            bound_params=tmp_cmdDef.bind,
            subcommands=resolved_subcommands,
            arguments=[arg for _, arg in new_arg_def_mapping.items()],
        )

        return resolved_cmdDef


    def resolve_argumentDef(self, argDef: ArgumentDef) -> ResolvedArgumentDef:
        #known, remaining = ResolvedArgumentDef.split_mapping(vars(argDef))
        resolved_argDef = ResolvedArgumentDef(
            argDef.key,
            definition=argDef,
            help=argDef.help,
            dest=argDef.dest,
            option=argDef.option,
            aliases=argDef.aliases,
            type=argDef.type,
            mult=argDef.mult,
            choices=argDef.choices,
            default=argDef.default,
            is_flag=argDef.is_flag,
            extra_defs=argDef.extra_defs,
            )
        #print(f"@@@@ resolve_argumentDef remaining: {remaining}")

        return resolved_argDef


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
                if item is not None and item._subcommands is None: # reject group
                    predecessors.append(item)
                else:
                    logging.warning(f"Could not resolve predecessor entry `{keyOrPath}` in inherit_from of CommandDef({cmdDef.defpath})")
        else: # fully inherit from templates
            predecessors.extend(cmdDef.get_templates())
        return predecessors


    # def bind_parameters(self, executable: ExecutableNode, resolved_):
    #     if executable.bind is not None:
    #         bind_mapping: dict[str, Any] = dict(executable.bind)
    #         # if isinstance(executable, CliDef|CommandDef):
    #         #     for argDef in executable.arguments:
    #         #         if argDef.key in bind_mapping:
    #         #             argDef.bound = bind_mapping.pop(argDef.key)
    #         # re-assign remaingings 
    #         # executable.bind = bind_mapping
