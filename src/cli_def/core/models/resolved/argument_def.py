# cli_def/core/models/resolved/argument_def.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Iterable, Sequence


from .resolved_node import ResolvedCliDefNode
from .resolved_protocols import ResolvedArgumentDefProtocol
from ..common.mult_def import MultDef
from ..raw.argument_def import ArgumentDef



# --------------------------------------------------------------------------------
# ResolvedArgumentDef
# a concrete class for argument/option representation of resoved model
# --------------------------------------------------------------------------------
class ResolvedArgumentDef(
    ResolvedCliDefNode,
    ResolvedArgumentDefProtocol
    ):

    _KNOWN_FIELDS = frozenset(
        ResolvedCliDefNode._KNOWN_FIELDS | {
        "dest",
        "option",
        "aliases",
        "type",
        "mult",
        "choices",
        "default",
        "is_flag",
    })

    BOUND_VALUE_SENTINEL = object()

    def __init__(
            self,
            key: str,
            *,
            definition: ArgumentDef,
            help: str|None = None,
            parent: ResolvedCliDefNode|None = None,

            dest: str|None = None,
            option: str|None = None,
            aliases: Iterable[str]|None = None,
            type: str|None = None,
            mult: str|int|MultDef|None = None,
            choices: Iterable[Any]|None = None,
            default: Any|None = None,
            is_flag: bool|None = None,

            bound_value: Any|None = BOUND_VALUE_SENTINEL,
            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(
            key,
            definition=definition,
            help=help,
            parent=parent,
            extra_defs=extra_defs
            )
        self._dest: str|None = dest
        self._option: str|None = option # "--<option>"
        self._aliases: list[str]|None = list(aliases) if aliases is not None else None
        self._type: str|None = type
        self._choices: list[Any]|None = list(choices) if choices is not None else None
        self._default: Any|None = default
        self._is_flag: bool|None = is_flag

        # fix mult
        tmp_mult: MultDef|None = MultDef.from_any(mult) if mult is not None else None
        self._mult: MultDef = (
            tmp_mult if tmp_mult is not None
            else MultDef(1, 1) if self.is_positional 
            else MultDef(0, 1)
        )
        # fix is_flag related
        if self._is_flag:
            if self._default is None:
                self._default = False
            if self._type is None:
                self._type = "bool"

        self._bound_value: Any|None = bound_value if bound_value is not self.BOUND_VALUE_SENTINEL else self.BOUND_VALUE_SENTINEL


    @property
    def dest(self) -> str|None:
        return self._dest
    @property
    def option(self) -> str|None:
        return self._option
    @property
    def aliases(self) -> Sequence[str]:
        return self._aliases or []
    @property
    def type(self) -> str|None:
        return self._type
    @property
    def mult(self) -> MultDef:
        return self._mult
    @property
    def choices(self) -> Sequence[Any]|None:
        return self._choices
    @property
    def default(self) -> Any|None:
        return self._default
    @property
    def is_flag(self) -> bool|None:
        return self._is_flag

    @property
    def is_leaf(self) -> bool:
        return True

    @property
    def is_positional(self) -> bool:
        return self.option is None


    @property
    def bound_value(self) -> Any|None:
        return self._bound_value

    @property
    def has_bound_value(self) -> bool:
        return self._bound_value is not self.BOUND_VALUE_SENTINEL


    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> ResolvedArgumentDef:

        known, remaining = cls.split_mapping(mapping)

        # 1) apply known
        obj = cls(**known)

        if remaining:
            obj._extra_defs.update(remaining)
        return obj


    def get_dest(self) -> str | None:
        if self.option is None:
            # positional parameter ignores dest
            return None
        return self.dest or self.key


    def get_action(self) -> str | None:
        if self.is_flag:
            if "action" in self.extra_defs:
                return self.extra_defs["action"]
            if self.default is not None and self.default == True:
                return "store_false"
            return "store_true"
        return None
