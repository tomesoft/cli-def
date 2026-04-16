# # cli_def/models/command_def.py
# from __future__ import annotations
# from typing import Iterable, Sequence, Mapping, Iterator, Any

# from .raw_protocols import RawCommandDefProtocol
# from ..generic.abstract_node import AbstractCliDefNode
# from ..generic.command_def import AbstractCommandDef
# from .argument_def import ArgumentDef
# # from .executable_node import ExecutableNode
# # from .argument_def import ArgumentDef



# # --------------------------------------------------------------------------------
# # CommandDef
# # a concrete class for command/subcommand definition
# # --------------------------------------------------------------------------------
# class CommandDef(AbstractCommandDef[ArgumentDef, AbstractCliDefNode], RawCommandDefProtocol):
#     # reserved keys
#     EARLY = "_early"

#     _KNOWN_FIELDS = AbstractCommandDef._KNOWN_FIELDS | {
#         "inherit_from",
#         "is_template",
#         "bind",
#     }

#     def __init__(
#             self,
#             key: str,
#             *,
#             help: str|None = None,
#             parent: AbstractCliDefNode|None = None,
#             entrypoint: str|None = None,
#             group: str|None = None,
#             bind: Mapping[str, Any]|None = None, # for parameter binding
#             arguments: Iterable[ArgumentDef]|None = None,

#             subcommands: Iterable[CommandDef]|None = None,
#             is_template: bool|None = None,
#             aliases: Iterable[str]|None = None,
#             inherit_from: Iterable[str]|None = None,

#             extra_defs: Mapping[str, Any]|None = None,
#         ):
#         super().__init__(
#             key,
#             help=help,
#             parent=parent,
#             entrypoint=entrypoint,
#             group=group,
#             arguments=arguments,
#             aliases=aliases,
#             subcommands=subcommands,
#             extra_defs=extra_defs
#             )
#         self._bind: dict[str, Any] = dict(bind) if bind else {}
#         self._inherit_from: list[str]|None = list(inherit_from) if inherit_from is not None else None

#         # fix is_template:
#         self._is_template: bool = (
#             is_template if is_template is not None
#             else self._key.startswith("_")
#         )

#     @property
#     def is_template(self) -> bool:
#         return self._is_template
    
#     @property
#     def inherit_from(self) -> Sequence[str]|None:
#         return self._inherit_from

#     @property
#     def bind(self) -> Mapping[str, Any]:
#         return self._bind


#     def merge_missing_from(self, other: CommandDef):
#         if self._help is None:
#             self._help = other.help
#         for k, v in other.extra_defs:
#             self._extra_defs.setdefault(k, v)

#         if self._entrypoint is None:
#             self._entrypoint = other.entrypoint
#         if self._group is None:
#             self._group = other.group
#         if self._bind is None:
#             if other.bind is not None:
#                 self._bind = dict(other.bind)
#         else:
#             if other.bind is not None:
#                 for k, v in other.bind.items():
#                     self._bind.setdefault(k, v)

#         if self.aliases is None:
#             if other.aliases is not None:
#                 self._aliases = list(other.aliases)


#     def override_with(self, other: CommandDef):
#         if other.help is not None:
#             self._help = other.help
#         self._extra_defs.update(other.extra_defs)

#         if other.entrypoint is not None:
#             self._entrypoint = other.entrypoint
#         if other.group is not None:
#             self._group = other.group
#         if other.bind is not None:
#             if self._bind is None:
#                 self._bind = dict(other.bind)
#             else:
#                 self._bind.update(other.bind)

#         if other.aliases:
#             self._aliases = list(other.aliases)



#     def get_templates(self) -> Sequence[CommandDef]:
#         templates = []
#         if self.parent:
#             for node in self.parent.iter_children():
#                 if isinstance(node, CommandDef) and node.is_template:
#                     templates.append(node)
#         if self.inherit_from is None:
#             return templates
#         inherit_set = set(self.inherit_from)
#         return [tmpl for tmpl in templates if tmpl.key in inherit_set]


#     def get_command_sequence(self) -> Sequence[str]:
#         key_seq = []
#         node = self
#         while node is not None:
#             key_seq.append(node.key)
#             node = node.parent
#         return list(reversed(key_seq))


# cli_def/models/command_def.py
from __future__ import annotations
from typing import Iterable, Sequence, Mapping, Iterator, Any, TypeVar, Self, Generic

from .raw_node import CliDefNode
from .executable_node import ExecutableNode
from .raw_protocols import RawCommandDefProtocol
from .argument_def import ArgumentDef

#TCmdDef = TypeVar("TCmdDef", bound="AbstractCommandDef")


# --------------------------------------------------------------------------------
# CommandDef
# an abstract class for command/subcommand definition
# --------------------------------------------------------------------------------
class CommandDef(
    ExecutableNode,
    RawCommandDefProtocol,
    ):

    # reserved keys
    EARLY = "_early"

    _KNOWN_FIELDS = frozenset(
        ExecutableNode._KNOWN_FIELDS | {
        "aliases",
        "inherit_from",
        "is_template",
    })


    def __init__(
            self,
            key: str,
            *,
            help: str|None = None,
            parent: CliDefNode|None = None,
            entrypoint: str|None = None,
            group: str|None = None,
            bind: Mapping[str, Any]|None = None, # for parameter binding
            arguments: Iterable[ArgumentDef]|None = None,

            subcommands: Iterable[CommandDef]|None = None,
            is_template: bool|None = None,
            aliases: Iterable[str]|None = None,
            inherit_from: Iterable[str]|None = None,

            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(
            key,
            help=help,
            parent=parent,
            entrypoint=entrypoint,
            group=group,
            arguments=arguments,
            bind=bind,
            extra_defs=extra_defs
            )
        self._aliases: list[str]|None = list(aliases) if aliases is not None else None
        self._inherit_from: list[str]|None = list(inherit_from) if inherit_from is not None else None
        self._subcommands: list[CommandDef]|None = list(subcommands) if subcommands is not None else None 
        self._aliases: list[str]|None = list(aliases) if aliases is not None else None

        # fix is_template:
        self._is_template: bool = (
            is_template if is_template is not None
            else self._key.startswith("_")
        )


    @property
    def is_template(self) -> bool:
        return self._is_template
    
    @property
    def inherit_from(self) -> Sequence[str]|None:
        return self._inherit_from

    @property
    def aliases(self) -> Sequence[str]:
        return self._aliases or []
    
    @property
    def subcommands(self) -> Sequence[CommandDef]:
        return self._subcommands or []

    @property
    def is_leaf(self) -> bool:
        return self._subcommands is None or len(self._subcommands) == 0


    def iter_children(self) -> Iterator[CliDefNode]:
        yield from super().iter_children()
        yield from self.subcommands or []


    def get_command_sequence(self) -> Sequence[str]:
        key_seq = []
        node = self
        while node is not None:
            key_seq.append(node.key)
            node = node.parent
        return list(reversed(key_seq))


    def merge_missing_from(self, other: CommandDef):
        if self._help is None:
            self._help = other.help
        for k, v in other.extra_defs:
            self._extra_defs.setdefault(k, v)

        if self._entrypoint is None:
            self._entrypoint = other.entrypoint
        if self._group is None:
            self._group = other.group
        if self._bind is None:
            if other.bind is not None:
                self._bind = dict(other.bind)
        else:
            if other.bind is not None:
                for k, v in other.bind.items():
                    self._bind.setdefault(k, v)

        if self.aliases is None:
            if other.aliases is not None:
                self._aliases = list(other.aliases)


    def override_with(self, other: CommandDef):
        if other.help is not None:
            self._help = other.help
        self._extra_defs.update(other.extra_defs)

        if other.entrypoint is not None:
            self._entrypoint = other.entrypoint
        if other.group is not None:
            self._group = other.group
        if other.bind is not None:
            if self._bind is None:
                self._bind = dict(other.bind)
            else:
                self._bind.update(other.bind)

        if other.aliases:
            self._aliases = list(other.aliases)



    def get_templates(self) -> Sequence[CommandDef]:
        templates = []
        if self.parent:
            for node in self.parent.iter_children():
                if isinstance(node, CommandDef) and node.is_template:
                    if node.key == self.EARLY:
                        continue
                    templates.append(node)
        return templates


