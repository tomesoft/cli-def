
# cli_def/core/models/raw/raw_protocols.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence
from typing import Protocol, TypeVar, Generic, Self

from ..common.mult_def import MultDef

from ..protocols import (
    CliDefNodeProtocol,
    # TreeViewProtocol,
    CommandDefProtocol,
    ArgumentDefProtocol,
    CliDefProtocol,
    ExecutableNodeProtocol,
)

# --------------------------------------------------------------------------------
# MutableNode protocol
# --------------------------------------------------------------------------------
TMutableNode = TypeVar("TMutableNode", bound="MutableNode")

class MutableNode(Protocol):

    def merge_missing_from(self: TMutableNode, other: TMutableNode):
        ...

    def override_with(self: TMutableNode, other: TMutableNode):
        ...


# --------------------------------------------------------------------------------
# RawCliDefNode protocol
# --------------------------------------------------------------------------------
TNode = TypeVar("TNode", bound="RawCliDefNodeProtocol")

class RawCliDefNodeProtocol(
    CliDefNodeProtocol,
    # TreeViewProtocol[TNode],
    MutableNode,
    Protocol #[TNode]
    ):
    pass

# --------------------------------------------------------------------------------
# RawArgumentDefProtocol protocol
# --------------------------------------------------------------------------------
class RawArgumentDefProtocol(RawCliDefNodeProtocol, ArgumentDefProtocol, Protocol):
    pass


# --------------------------------------------------------------------------------
# RawExecutableNodeProtocol protocol
# --------------------------------------------------------------------------------
class RawExecutableNodeProtocol(
    RawCliDefNodeProtocol,
    ExecutableNodeProtocol[RawArgumentDefProtocol],
    Protocol
    ):

    @property
    def bind(self) -> Mapping[str, Any]:
        ...


# --------------------------------------------------------------------------------
# RawCommandDefProtocol protocol
# --------------------------------------------------------------------------------
class RawCommandDefProtocol(
    RawExecutableNodeProtocol,
    CommandDefProtocol[RawArgumentDefProtocol],
    Protocol
    ):

    @property
    def inherit_from(self) -> Sequence[str]:
        ...

    @property
    def is_template(self) -> bool:
        ...


# --------------------------------------------------------------------------------
# RawCliDefProtocol protocol
# --------------------------------------------------------------------------------
class RawCliDefProtocol(
    RawExecutableNodeProtocol,
    CliDefProtocol[RawArgumentDefProtocol, RawCommandDefProtocol],
    Protocol
    ):

    @property
    def include(self) -> Sequence[str]:
        ...

