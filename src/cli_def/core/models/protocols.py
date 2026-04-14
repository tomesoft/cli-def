# cli_def/core/models/protocols.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence
from typing import Protocol, TypeVar, Generic, Self

from .common.mult_def import MultDef


TNode_co = TypeVar(
    "TNode_co",
    bound="CliDefNodeProtocol",
    covariant=True
)

# --------------------------------------------------------------------------------
# CliDefNode protocol
# --------------------------------------------------------------------------------
class CliDefNodeProtocol(Protocol):

    @property
    def key(self) -> str:
        ...

    @property
    def help(self) -> str|None:
        ...

    @property
    def parent(self) -> Self|None:
        ...

    @property
    def extra_defs(self) -> Mapping[str, Any]:
        ...

    @property
    def defpath(self) -> str:
        ...

    @property
    def deflevel(self) -> int:
        ...

    @property
    def is_leaf(self) -> bool:
        ...


# --------------------------------------------------------------------------------
# TreeView protocol
# --------------------------------------------------------------------------------
class TreeViewProtocol(Protocol[TNode_co]):

    def iter_all_nodes(self) -> Iterator[TNode_co]:
        ...

    def iter_children(self) -> Iterator[TNode_co]:
        ...

    def find_by_defpath(
            self,
            defpath: str
        ) -> TNode_co|None:
        ...

    def select_first(
            self,
            pred: Callable[[TNode_co], Any]
        ) -> TNode_co|None:
        ...

    def select_all(
            self,
            pred: Callable[[TNode_co], Any]
        ) -> Iterable[TNode_co]:
        ...


# --------------------------------------------------------------------------------
# ArgumentDefProtocol protocol
# --------------------------------------------------------------------------------
class ArgumentDefProtocol(Protocol):

    @property
    def dest(self) -> str|None:
        ...
    @property
    def option(self) -> str|None:
        ...
    @property
    def aliases(self) -> Sequence[str]:
        ...
    @property
    def type(self) -> str|None:
        ...
    @property
    def mult(self) -> MultDef:
        ...
    @property
    def choices(self) -> Sequence[Any]|None:
        ...
    @property
    def default(self) -> Any|None:
        ...
    @property
    def is_flag(self) -> bool|None:
        ...


# --------------------------------------------------------------------------------
# ExecutableNodeProtocol protocol
# --------------------------------------------------------------------------------
TArgDef = TypeVar("TArgDef", bound="ArgumentDefProtocol")
class ExecutableNodeProtocol(Protocol[TArgDef]):
    @property
    def entrypoint(self) -> str|None:
        ...
    @property
    def group(self) -> str|None:
        ...
    @property
    def arguments(self) -> Sequence[TArgDef]:
        ...


# --------------------------------------------------------------------------------
# CommandDefProtocol protocol
# --------------------------------------------------------------------------------
class CommandDefProtocol(ExecutableNodeProtocol[TArgDef], Protocol[TArgDef]):

    @property
    def aliases(self) -> Sequence[str]:
        ...
    @property
    def subcommands(self) -> Sequence[Self]:
        ...


# --------------------------------------------------------------------------------
# CliDefProtocol protocol
# --------------------------------------------------------------------------------
TCmdDef = TypeVar("TCmdDef", bound="CommandDefProtocol[Any]")
class CliDefProtocol(ExecutableNodeProtocol[TArgDef], Protocol[TArgDef, TCmdDef]):

    @property
    def prompt(self) -> str|None:
        ...
    @property
    def commands(self) -> Sequence[TCmdDef]:
        ...

