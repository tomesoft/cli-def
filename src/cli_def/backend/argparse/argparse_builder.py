# cli_def/backend/argparse/argparse_builder.py
from typing import Iterable, Sequence, Any, Mapping
import argparse
import logging

from ...core.models import (
    CliDefNode,
    CliDef,
    ArgumentDef,
    CommandDef,
)
from ...core.models import (
    ResolvedCliDefNode,
    ResolvedCliDef,
    ResolvedCommandDef,
    ResolvedExecutableNode,
    ResolvedArgumentDef,
    MultDef,
)

from typing import Union

ArgparseNode = Union[
    argparse.ArgumentParser,
    argparse._SubParsersAction,
    argparse.Action,
]

from ..protocols import BuilderProtocol


class ArgparseBuilder(BuilderProtocol):

    def __init__(self):
        self._defpath_mapping: dict[str, ArgparseNode] = {}
        self._early_parser = None

    @property
    def defpath_mapping(self) -> Mapping[str, ArgparseNode]:
        return self._defpath_mapping


    def build(self, cliDef: ResolvedCliDef) -> argparse.ArgumentParser:
        return self.build_argparse(cliDef)


    def _register(self, node: ResolvedCliDefNode, obj: Any):
        self._defpath_mapping[node.defpath] = obj


    def _register_subparsers(self, node: ResolvedCliDefNode, obj: Any):
        special_defpath = "/".join([node.defpath, "__subparsers__"])
        self._defpath_mapping[special_defpath] = obj


    def build_early_argparse(self, cliDef: CliDef, prog: str|None = None) -> argparse.ArgumentParser|None:
        early_node = cliDef.select_first(lambda n: n.key == CommandDef.EARLY)

        parser = argparse.ArgumentParser(
            prog=prog or cliDef.key,
            add_help=False,
        )
        assert isinstance(early_node, CommandDef)
        self.build_arguments(early_node.arguments, parser)
        return parser


    def build_argparse(self, cliDef: ResolvedCliDef, prog: str|None = None) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=prog or cliDef.key
        )

        self._register(cliDef, parser)

        self.build_arguments(cliDef.arguments, parser)
        if cliDef.commands:
            self.build_commands(cliDef.commands, parser)

        self._attach_metadata(parser, cliDef, cliDef.get_command_sequence())

        return parser


    def build_arguments(
            self,
            argumentDefs: Iterable[ResolvedArgumentDef]|Iterable[ArgumentDef],
            parser: argparse.ArgumentParser,
            ) -> Iterable[argparse.Action] | None:
        if argumentDefs is None:
            return None
        actions = []
        for argDef in argumentDefs:
            if hasattr(argDef, "has_bound_value") and getattr(argDef, "has_bound_value"):
                continue # skip bound parameters

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
                    *name_or_flags,
                    dest=argDef.get_dest(),
                    help=argDef.help,
                    action=argDef.get_action() or "",
                )
            else: # option parameter
                name_or_flags = []
                if argDef.aliases:
                    name_or_flags.extend(argDef.aliases)
                name_or_flags.append(argDef.option)
                action = parser.add_argument(
                    *name_or_flags,
                    dest=argDef.get_dest(),
                    choices=argDef.choices,
                    default=argDef.default,
                    nargs=self.to_nargs(argDef.mult),
                    help=argDef.help,
                )

            actions.append(action)
            if isinstance(argDef, ResolvedArgumentDef):
                self._register(argDef, action)

        return actions


    def build_commands(
            self,
            commandDefs: Sequence[ResolvedCommandDef],
            parser: argparse.ArgumentParser,
            ) -> Iterable[argparse.ArgumentParser] | None:
        if commandDefs is None or len(commandDefs) == 0:
            return None

        firstCmdDef: ResolvedCommandDef = commandDefs[0]
        assert isinstance(firstCmdDef.parent, ResolvedExecutableNode)
        group = (firstCmdDef.parent.group or
                ("sub" * firstCmdDef.parent.deflevel) + "command"
        )

        subparsers = parser.add_subparsers(dest=group) 
        self._register_subparsers(firstCmdDef.parent, subparsers)
        cmd_parsers = []
        for cmdDef in commandDefs:
            cmd_parser = self.build_single_command(cmdDef, subparsers)
            cmd_parsers.append(cmd_parser)

        return cmd_parsers


    def build_single_command(
            self,
            cmdDef: ResolvedCommandDef,
            subparsers: argparse._SubParsersAction|None = None,
            parent_parsers: Sequence[argparse.ArgumentParser]|None = None
            ) -> argparse.ArgumentParser:
        if parent_parsers is None:
            parent_parsers = []
        if subparsers is not None:
            parser = subparsers.add_parser(
                cmdDef.key,
                help = cmdDef.help,
                parents=parent_parsers,
            )
        else:
            # kwargs = ({"add_help":True:cmdDef.help}
            #         if cmdDef.help is not None else
            #         {"add_help":False}
            # )
            parser = argparse.ArgumentParser(
                cmdDef.key,
                parents=parent_parsers,
                add_help=True if cmdDef.help is not None else False,
                # **kwargs
            )
        self.build_arguments(cmdDef.arguments, parser)
        if cmdDef.subcommands:
            self.build_commands(cmdDef.subcommands, parser)

        self._register(cmdDef, parser)
        self._attach_metadata(parser, cmdDef, cmdDef.get_command_sequence())

        return parser


    def _attach_metadata(self, parser, command: ResolvedCommandDef|ResolvedCliDef, path):
        parser.set_defaults(
            _path=path,
            _command=command,
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