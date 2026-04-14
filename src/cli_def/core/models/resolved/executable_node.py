# # cli_def/core/models/resolved/cli_def_node.py
# from __future__ import annotations
# from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence, Protocol

# from ..protocols import MutableNode
# from ..common.abstract_node import AbstractCliDefNode
# from ..common.executable_node import AbstractExecutableNode
# from .argument_def import ArgumentDef

# # --------------------------------------------------------------------------------
# # ExecutableNode abstract class
# # common base class of CliDef and CommandDef
# # --------------------------------------------------------------------------------
# class ExecutableNode(AbstractExecutableNode, MutableNode):

#     _KNOWN_FIELDS = AbstractExecutableNode._KNOWN_FIELDS | {
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
#             arguments: Iterable[ArgumentDef]|None = None,
#             bind: Mapping[str, Any]|None = None, # for parameter binding
#             extra_defs: Mapping[str, Any]|None = None,
#         ):
#         super().__init__(key, help=help, parent=parent, extra_defs=extra_defs)
#         self._entrypoint: str|None = entrypoint
#         self._group: str|None = group
#         self._arguments: list[ArgumentDef] = list(arguments) if arguments else []
#         self._bind: dict[str, Any] = dict(bind) if bind else {}

#     @property
#     def entrypoint(self) -> str|None:
#         return self._entrypoint

#     @property
#     def group(self) -> str|None:
#         return self._group

#     @property
#     def arguments(self) -> Sequence[ArgumentDef]:
#         return self._arguments

#     @property
#     def bind(self) -> Mapping[str, Any]:
#         return self._bind


#     def merge_missing_from(self, other: ExecutableNode):
#         super().merge_missing_from(other)
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


#     def override_with(self, other: ExecutableNode):
#         super().override_with(other)
#         if other.entrypoint is not None:
#             self._entrypoint = other.entrypoint
#         if other.group is not None:
#             self._group = other.group
#         if other.bind is not None:
#             if self._bind is None:
#                 self._bind = dict(other.bind)
#             else:
#                 self._bind.update(other.bind)


#     def iter_children(self) -> Iterator[CliDefNode]:
#         yield from self._arguments or []
# cli_def/core/models/resolved/executable_node.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence, TypeVar, Generic

from ..raw.raw_node import CliDefNode
from .resolved_node import ResolvedCliDefNode
from .resolved_protocols import ResolvedExecutableNodeProtocol
from .argument_def import ResolvedArgumentDef


#TArgDef = TypeVar("TArgDef", bound="AbstractArgumentDef")
# --------------------------------------------------------------------------------
# AbstractExecutableNode abstract class
# common base class of CliDef and CommandDef
# --------------------------------------------------------------------------------
class ResolvedExecutableNode(
    ResolvedCliDefNode,
    ResolvedExecutableNodeProtocol,
    ):

    _KNOWN_FIELDS = frozenset(
        ResolvedCliDefNode._KNOWN_FIELDS | {
        "entrypoint",
        "group",
        "bound_params",
    })

    def __init__(
            self,
            key: str,
            *,
            definition: CliDefNode,
            help: str|None = None,
            parent: ResolvedCliDefNode|None = None,
            entrypoint: str|None = None,
            group: str|None = None,
            arguments: Iterable[ResolvedArgumentDef]|None = None,
            bound_params: Mapping[str, Any]|None = None, # for parameter binding
            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(
            key,
            definition=definition,
            help=help,
            parent=parent,
            extra_defs=extra_defs)
        self._entrypoint: str|None = entrypoint
        self._group: str|None = group
        self._arguments: list[ResolvedArgumentDef] = list(arguments) if arguments else []
        self._bound_params: dict[str, Any] = dict(bound_params) if bound_params else {}

        # fix arguments' parents
        if self._arguments:
            for n in self._arguments:
                n._parent = self

        # fix bound_values of arguments
        if self._arguments and self.bound_params:
            for n in self._arguments:
                if n.key in self.bound_params:
                    n._bound_value = self.bound_params[n.key]


    @property
    def entrypoint(self) -> str|None:
        return self._entrypoint

    @property
    def group(self) -> str|None:
        return self._group

    @property
    def arguments(self) -> Sequence[ResolvedArgumentDef]:
        return self._arguments

    @property
    def bound_params(self) -> Mapping[str, Any]:
        return self._bound_params

    def iter_children(self) -> Iterator[ResolvedCliDefNode]:
        yield from self._arguments or []