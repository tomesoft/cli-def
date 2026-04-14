
# cli_def/core/models/resolved/resolved_protocols.py
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
# ResolvedNode protocol
# --------------------------------------------------------------------------------
class ResolvedCliDefNodeProtocol(
    CliDefNodeProtocol,
    # TreeViewProtocol["ResolvedNode"],
    Protocol
    ):

    @property
    def definition(self) -> CliDefNodeProtocol:
        ...


# --------------------------------------------------------------------------------
# ResolvedArgumentDefProtocol protocol
# --------------------------------------------------------------------------------
class ResolvedArgumentDefProtocol(ResolvedCliDefNodeProtocol, ArgumentDefProtocol, Protocol):
    
    @property
    def bound_value(self) -> Any|None:
        ...
    @property
    def has_bound_value(self) -> bool:
        ...


# --------------------------------------------------------------------------------
# ResolvedExecutableNodeProtocol protocol
# --------------------------------------------------------------------------------
class ResolvedExecutableNodeProtocol(
    ResolvedCliDefNodeProtocol,
    ExecutableNodeProtocol[ResolvedArgumentDefProtocol],
    Protocol):
    
    @property
    def bound_params(self) -> Mapping[str, Any]:
        ...


# --------------------------------------------------------------------------------
# ResolvedCommandDefProtocol protocol
# --------------------------------------------------------------------------------
class ResolvedCommandDefProtocol(
    ResolvedExecutableNodeProtocol,
    CommandDefProtocol[ResolvedArgumentDefProtocol],
    Protocol
    ):
    pass   


# --------------------------------------------------------------------------------
# ResolvedCliDefProtocol protocol
# --------------------------------------------------------------------------------
class ResolvedCliDefProtocol(
    ResolvedExecutableNodeProtocol,
    CliDefProtocol[ResolvedArgumentDefProtocol, ResolvedCommandDefProtocol],
    Protocol):
    pass
