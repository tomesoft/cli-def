# cli_def/core/validator/validator.py
from __future__ import annotations
from typing import Any, Sequence, Iterable
from enum import Enum, auto
from dataclasses import dataclass

from ..models import (
    ResolvedCliDef,
    ResolvedCommandDef,
    ResolvedArgumentDef,
    ResolvedCliDefNode,
    MultDef,
)

class CliDefValidationLevel(Enum):
    ERROR = auto()
    WARNING = auto()

    def __str__(self) -> str:
        return self.name


class CliDefValidationCategory(Enum):
    CLI = auto()
    CMD = auto()
    ARG = auto()

    def __str__(self) -> str:
        return self.name


class CliDefValidationCode(Enum):
    E_ARG_BOUND_TYPE_ERROR = (auto(), CliDefValidationCategory.ARG, CliDefValidationLevel.ERROR)
    E_ARG_NOT_IN_CHOICES = (auto(), CliDefValidationCategory.ARG, CliDefValidationLevel.ERROR)
    E_ARG_MULT_ERROR = (auto(), CliDefValidationCategory.ARG, CliDefValidationLevel.ERROR)

    E_CMD_DUPLICATE_OPTION = (auto(), CliDefValidationCategory.CMD, CliDefValidationLevel.ERROR)
    E_CMD_CONFLICT_ALIAS = (auto(), CliDefValidationCategory.CMD, CliDefValidationLevel.ERROR)
    W_CMD_UNUSED_BIND = (auto(), CliDefValidationCategory.CMD, CliDefValidationLevel.WARNING)

    def __init__(self, id, category, level):
        self.id = id
        self.category = category
        self.level = level

    def __str__(self) -> str:
        return self.name

# class CliDefValidationCode(Enum):
#     E_ERROR_START = auto()
#     # cli_def
#     E_CLI_START = auto()
#     E_CLI_END = auto()
#     # command
#     E_CMD_START = auto()
#     E_CMD_END = auto()
#     # argument
#     E_ARG_START = auto()
#     E_ARG_BOUND_VALUE_TYPE_ERROR = auto()
#     E_ARG_BOUND_VALUE_NOT_IN_CHOICES = auto()
#     E_ARG_BOUND_VALUE_MULT_ERROR = auto()
#     E_ARG_END = auto()
#     E_ERROR_END = auto()

#     W_WARNING_START = auto()
#     W_ARG_UNUSED_BIND = auto()
#     W_DUPLICATE_OPTION = auto()
#     W_WARNING_END = auto()


#     def __str__(self) -> str:
#         return self.name


@dataclass
class CliDefValidationRecord:
    code: CliDefValidationCode
    node: ResolvedCliDefNode
    message: str

    def __str__(self) -> str:
        return f"({str(self.code), {self.node.defpath}, {self.message}})"


class CliDefValidator:

    def __init__(self):
        self._records: list[CliDefValidationRecord] = []

    @property
    def has_errors(self) -> bool:
        return len(self._records) > 0

    @property
    def records(self) -> Sequence[CliDefValidationRecord]:
        return self._records

    @property
    def errors(self) -> Sequence[CliDefValidationCode]:
        return [r.code for r in self._records]

    def clear_errors(self):
        self._records.clear()

    def _register(self, record: CliDefValidationRecord):
        self._records.append(record)


    def validate_cli(self, cli_def: ResolvedCliDef):

        # 1) check self

        # 2) check arguments
        for arg in cli_def.arguments:
            self.validate_arg(arg)

        # 3) check commands
        for cmd in cli_def.commands:
            self.validate_cmd(cmd)


    def validate_cmd(self, cmd: ResolvedCommandDef):

        # 1) check self
        argument_keys = {a.key for a in cmd.arguments}
        for k, _ in cmd.bound_params.items():
            if k not in argument_keys:
                self._register(
                    CliDefValidationRecord(
                        CliDefValidationCode.W_CMD_UNUSED_BIND,
                        cmd,
                        f"{k!r} target not found"
                    )
                )
        seen_options: set[str] = set()
        for arg in cmd.arguments:
            if arg.option is None:
                continue
            if arg.has_bound_value:
                continue
            if arg.option not in seen_options:
                seen_options.add(arg.option)
            else:
                self._register(
                    CliDefValidationRecord(
                        CliDefValidationCode.E_CMD_DUPLICATE_OPTION,
                        cmd,
                        f"dupliate option '{arg.option}'"
                    )
                )

        seen_aliases: set[str] = set()
        for arg in cmd.arguments:
            if arg.aliases == []:
                continue
            if arg.has_bound_value:
                continue
            for alias in arg.aliases:
                if alias not in seen_aliases:
                    seen_aliases.add(alias)
                else:
                    self._register(
                        CliDefValidationRecord(
                            CliDefValidationCode.E_CMD_CONFLICT_ALIAS,
                            cmd,
                            f"conflict alias '{alias}'"
                        )
                    )


        # 2 check arguments
        for arg in cmd.arguments:
            self.validate_arg(arg)
        # 3) check subcommands
        for subcmd in cmd.subcommands:
            self.validate_cmd(subcmd)


    def validate_arg(self, arg: ResolvedArgumentDef):

        # 1) bound_params
        if arg.has_bound_value:
            bound_value = arg.bound_value
            # 1.1) type check
            if not self.check_arg_type(bound_value, arg.type):
                self._register(
                    CliDefValidationRecord(
                        CliDefValidationCode.E_ARG_BOUND_TYPE_ERROR,
                        arg,
                        f"expected={arg.type}, got={type(bound_value).__name__} (value={bound_value!r})",
                    )
                )
            # 1.2) choices check
            if arg.choices:
                if bound_value not in arg.choices:
                    self._register(
                        CliDefValidationRecord(
                            CliDefValidationCode.E_ARG_NOT_IN_CHOICES,
                            arg,
                            f"value={bound_value!r} not in choices {arg.choices!r}",
                        )
                    )
            # 1.3) mult check
            if not self.accepts_value_mult(bound_value, arg.mult):
                self._register(
                    CliDefValidationRecord(
                        CliDefValidationCode.E_ARG_MULT_ERROR,
                        arg,
                        f"{bound_value!r} can not accept mult {arg.mult.to_tuple()}",
                    )
                )


    def check_arg_type(self, val: Any, type: str|None) -> bool:
        if isinstance(val, list):
            return all([self.check_arg_type(e, type) for e in val])
        if type == "int":
            return isinstance(val, int)
        if type == "float":
            return isinstance(val, float)
        if type == "bool":
            return isinstance(val, bool)
        if type == "str":
            return isinstance(val, str)
        return True # Any


    def accepts_value_mult(self, val: Any, mult: MultDef) -> bool:
        mul = 0
        if isinstance(val, str):
            mul = 1
        elif isinstance(val, list): # expect from TOML
            mul = len(val)
        else:
            mul = 1
        return mult.accepts_len(mul)
