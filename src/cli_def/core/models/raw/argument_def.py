# cli_def/core/models/raw/argument_def.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Iterable, Sequence, Generic


from .raw_node import CliDefNode
from .raw_protocols import RawArgumentDefProtocol
from ..common.mult_def import MultDef



# --------------------------------------------------------------------------------
# ArgumentDef
# a concrete class for argument/option definition or raw model
# --------------------------------------------------------------------------------
class ArgumentDef(
    CliDefNode,
    RawArgumentDefProtocol,
    ):

    _KNOWN_FIELDS = frozenset(
        CliDefNode._KNOWN_FIELDS | {
        "dest",
        "option",
        "aliases",
        "type",
        "mult",
        "choices",
        "default",
        "is_flag",
    })

    def __init__(
            self,
            key: str,
            *,
            help: str|None = None,
            parent: CliDefNode|None = None,

            dest: str|None = None,
            option: str|None = None,
            aliases: Iterable[str]|None = None,
            type: str|None = None,
            mult: str|int|MultDef|None = None,
            choices: Iterable[Any]|None = None,
            default: Any|None = None,
            is_flag: bool|None = None,

            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(key, help=help, parent=parent, extra_defs=extra_defs)

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


    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> ArgumentDef:

        known, remaining = cls.split_mapping(mapping)

        # 1) apply known
        obj = cls(**known)

        if remaining:
            obj._extra_defs.update(remaining)
        return obj


    def iter_children(self) -> Iterator[CliDefNode]:
        return iter([])


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


    def merge_missing_from(self, other: ArgumentDef):
        if self._help is None:
            self._help = other.help
        for k, v in other.extra_defs:
            self._extra_defs.setdefault(k, v)

        if self._dest is None:
            self._dest = other.dest
        if self._option is None:
            self._option = other.option
        if self._aliases is None:
            self._aliases = list(other.aliases)
        if self._type is None:
            self._type = other.type
        if self._mult is None:
            self._mult = other.mult
        if self._choices is None:
            self._choices = list(other.choices) if other.choices else None
        if self._default is None:
            self._default = other.default
        if self._is_flag is None:
            self._is_flag = other.is_flag


    def override_with(self, other: ArgumentDef):
        if other.help is not None:
            self._help = other.help
        self._extra_defs.update(other.extra_defs)

        if other.dest is not None:
            self._dest = other.dest
        if other.option is not None:
            self._option = other.option
        if other.aliases is not None:
            self._aliases = list(other.aliases)
        if other.type is not None:
            self._type = other.type
        if other.mult is not None:
            self._mult = other.mult
        if other.choices is not None:
            self._choices = list(other.choices)
        if other.default is not None:
            self._default = other.default
        if other.is_flag is not None:
            self._is_flag = other.is_flag
