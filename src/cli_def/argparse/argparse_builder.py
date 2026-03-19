# cli_def/argparse/argparse_builder.py
from typing import Iterable, Sequence, Any, Mapping
import argparse

from ..models import (
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

    def _register(self, node: CliDefNode, obj: Any):
        self._defpath_mapping[node.defpath] = obj

    def _register_subparsers(self, node: CliDefNode, obj: Any):
        special_defpath = "/".join([node.defpath, "__subparsers__"])
        self._defpath_mapping[special_defpath] = obj


    @property
    def defpath_mapping(self) -> Mapping[str, ArgparseNode]:
        return self._defpath_mapping

    def build_argparse(self, cliDef: CliDef) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()

        self._register(cliDef, parser)

        self.build_arguments(cliDef.arguments, parser)
        self.build_commands(cliDef.commands, parser)

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
            print(f"{argDef.defpath} mult={argDef.mult} nargs={self.to_nargs(argDef.mult)}")
            if argDef.is_positional:
                # positional paremter
                action = parser.add_argument(
                    argDef.key,
                    # dest=argDef.get_dest(),
                    choices=argDef.choices,
                    default=argDef.default,
                    #nargs=argDef.mult,
                    nargs=self.to_nargs(argDef.mult),
                    help=argDef.help,
                    #action=argDef.get_action(),
                    #action=None,
                )
            elif argDef.is_flag:
                action = parser.add_argument(
                    argDef.option or argDef.key,
                    dest=argDef.get_dest(),
                    #nargs=argDef.mult,
                    #nargs=argDef.to_nargs(),
                    help=argDef.help,
                    action=argDef.get_action(),
                    #action=None,
                )
            else: # option parameter
                action = parser.add_argument(
                    argDef.option,
                    dest=argDef.get_dest(),
                    choices=argDef.choices,
                    default=argDef.default,
                    #nargs=argDef.mult,
                    nargs=self.to_nargs(argDef.mult),
                    help=argDef.help,
                    #action=argDef.get_action(),
                    #action=None,
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

        # build parent parsers from of template
        parent_parsers = []
        for cmdDef in commandDefs:
            if not cmdDef.is_template:
                continue
            cmd_templ_parser = self.build_single_command(cmdDef)
            parent_parsers.append(cmd_templ_parser)
            
        firstCmdDef: CommandDef = commandDefs[0]
        group = (firstCmdDef.parent.group or
                ("sub" * firstCmdDef.parent.deflevel) + "command"
        )

        subparsers = parser.add_subparsers(dest=group) 
        self._register_subparsers(firstCmdDef.parent, subparsers)
        cmd_parsers = []
        for cmdDef in commandDefs:
            if cmdDef.is_template:
                continue
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

        return parser

    def to_nargs(self, mult: MultDef) -> str | int | None:
        if mult is None:
            return None

        if mult.is_fixed: # lower == upper
            return mult.lower

        if mult.is_optional:
            return "?"

        if mult.is_unbounded:
            if mult.lower == 0:
                return "*"
            elif mult.lower == 1:
                return "+"
        
        return f"{mult.lower}..{mult.upper}"