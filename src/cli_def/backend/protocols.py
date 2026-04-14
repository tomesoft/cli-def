# cli_def/backend/protocols.py

from typing import Protocol, Mapping

from ..core.models import ResolvedCliDef


class BuilderProtocol(Protocol):

    @property
    def defpath_mapping(self) -> Mapping[str, object]:
        ...

    def build(self, cliDef: ResolvedCliDef) -> object:
        ...



class BinderProtocol(Protocol):

    def bind(self, defpath_mapping: Mapping[str, object]):
        ...