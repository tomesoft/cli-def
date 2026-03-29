# cli_def/backend/argparse/argparse_builder.py
from typing import Iterable, Sequence, Any, Mapping
import argparse
import logging

from ...models import (
    CliDefNode,
    CliDef,
    CommandDef,
    ArgumentDef,
    MultDef,
)

from typing import Union

ArgparseNode = Union[
    argparse.ArgumentParser,
    argparse._SubParsersAction,
    argparse.Action,
]

class ArgparseBuilder:

    def __init__(self):
        self._defpath_mapping: dict[str, ArgparseNode] = {}
        self._early_parser = None

    def _register(self, node: CliDefNode, obj: Any):
        self._defpath_mapping[node.defpath] = obj

    def _register_subparsers(self, node: CliDefNode, obj: Any):
        special_defpath = "/".join([node.defpath, "__subparsers__"])
        self._defpath_mapping[special_defpath] = obj


    @property
    def defpath_mapping(self) -> Mapping[str, ArgparseNode]:
        return self._defpath_mapping


    def build_early_argparse(self, cliDef: CliDef, prog: str = None) -> argparse.ArgumentParser:
        early_node: CommandDef = cliDef.select_first(lambda n: n.key == CommandDef.EARLY)
        if early_node is None:
            return None

        parser = argparse.ArgumentParser(
            prog=prog or cliDef.key,
            add_help=False,
        )
        self.build_arguments(early_node.arguments, parser)
        return parser


    def build_argparse(self, cliDef: CliDef, prog: str = None) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=prog or cliDef.key
        )

        self._register(cliDef, parser)

        self.build_arguments(cliDef.arguments, parser)
        self.build_commands(cliDef.commands, parser)

        self._attach_metadata(parser, cliDef, cliDef.get_command_sequence())

        return parser


    def build_arguments(
            self,
            argumentDefs: Iterable[ArgumentDef],
            parser: argparse.ArgumentParser,
            ) -> Iterable[argparse.Action] | None:
        if argumentDefs is None:
            return None
        actions = []
        for argDef in argumentDefs:
            logging.debug(f"{argDef.defpath} mult={argDef.mult} nargs={self.to_nargs(argDef.mult)}")
            if argDef.is_positional:
                # positional paremter
                action = parser.add_argument(
                    argDef.key,
                    choices=argDef.choices,
                    default=argDef.default,
                    nargs=self.to_nargs(argDef.mult),
                    help=argDef.help,
                )
            elif argDef.is_flag:
                name_or_flags = []
                if argDef.aliases:
                    name_or_flags.extend(argDef.aliases)
                name_or_flags.append(argDef.option or argDef.key)
                action = parser.add_argument(
                    #argDef.option or argDef.key,
                    *name_or_flags,
                    dest=argDef.get_dest(),
                    help=argDef.help,
                    action=argDef.get_action(),
                )
            else: # option parameter
                name_or_flags = []
                if argDef.aliases:
                    name_or_flags.extend(argDef.aliases)
                name_or_flags.append(argDef.option)
                action = parser.add_argument(
                    #argDef.option,
                    *name_or_flags,
                    dest=argDef.get_dest(),
                    choices=argDef.choices,
                    default=argDef.default,
                    nargs=self.to_nargs(argDef.mult),
                    help=argDef.help,
                )

            actions.append(action)
            self._register(argDef, action)

        return actions


    def build_commands(
            self,
            commandDefs: Sequence[CommandDef],
            parser: argparse.ArgumentParser,
            ) -> Iterable[argparse.ArgumentParser] | None:
        if commandDefs is None or len(commandDefs) == 0:
            return None

        # build parent parsers from defs of templates
        parent_parsers_map = {}
        for cmdDef in commandDefs:
            if not cmdDef.is_template or cmdDef.key == CommandDef.EARLY:
                continue
            cmd_templ_parser = self.build_single_command(cmdDef)
            parent_parsers_map[cmdDef.key] = cmd_templ_parser
            if cmdDef.key == CommandDef.EARLY:
                #print(f"@@@ early_parser found :{cmdDef.key}")
                self._early_parser = cmd_templ_parser
            
        firstCmdDef: CommandDef = commandDefs[0]
        group = (firstCmdDef.parent.group or
                ("sub" * firstCmdDef.parent.deflevel) + "command"
        )

        subparsers = parser.add_subparsers(dest=group) 
        self._register_subparsers(firstCmdDef.parent, subparsers)
        cmd_parsers = []
        for cmdDef in commandDefs:
            if cmdDef.is_template or cmdDef.key == CommandDef.EARLY:
                continue
            # select parent_parsers
            parent_parsers = []
            for tmpl in cmdDef.get_templates():
                if tmpl.key in parent_parsers_map:
                    #print(f"@@@ parent_parser :{tmpl.key}")
                    parent_parsers.append(parent_parsers_map[tmpl.key])
            # # TODO consider forcibly add _early to parents
            # #print(f"@@@ self_early_parser = {"None" if self._early_parser is None else "Not None"}")
            # if self._early_parser and self._early_parser not in parent_parsers:
            #     #print(f"@@@ add _early parser to {cmdDef.defpath}")
            #     parent_parsers.append(self._early_parser)

            cmd_parser = self.build_single_command(cmdDef, subparsers, parent_parsers)
            cmd_parsers.append(cmd_parser)

        return cmd_parsers


    def build_single_command(
            self,
            cmdDef: CommandDef,
            subparsers: argparse._SubParsersAction|None = None,
            parent_parsers: list[argparse.ArgumentParser]|None = None
            ) -> Any:
        if parent_parsers is None:
            parent_parsers = []
        if subparsers is not None:
            parser = subparsers.add_parser(
                cmdDef.key,
                help = cmdDef.help,
                parents=parent_parsers,
            )
        else:
            kwargs = ({"add_help":True, "help":cmdDef.help}
                    if cmdDef.help is not None else
                    {"add_help":False}
            )
            parser = argparse.ArgumentParser(
                cmdDef.key,
                parents=parent_parsers,
                **kwargs
            )
        self.build_arguments(cmdDef.arguments, parser)
        self.build_commands(cmdDef.subcommands, parser)

        self._register(cmdDef, parser)
        self._attach_metadata(parser, cmdDef, cmdDef.get_command_sequence())

        return parser

    def _attach_metadata(self, parser, command: CommandDef, path):
        parser.set_defaults(
            _path=path,
            _command=command,   # ← これも入れる（重要）
        )

    def to_nargs(self, mult: MultDef) -> str | int | None:
        if mult is None:
            return None

        if mult.is_fixed: # lower == upper
            if mult.lower == 1:
                return None # to fix problem list ['param'] passing
            return mult.lower

        if mult.is_optional:
            return "?"

        if mult.is_unbounded:
            if mult.lower == 0:
                return "*"
            elif mult.lower == 1:
                return "+"
        
        return f"{mult.lower}..{mult.upper}"