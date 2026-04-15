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

class CliDefValidationError(Enum):
    # cli_def
    E_CLI_X = auto()
    # command
    E_CMD_X = auto()
    # argument
    E_ARG_X = auto()
    E_ARG_BOUND_VALUE_TYPE_ERROR = auto()
    E_ARG_BOUND_VALUE_NOT_IN_CHOICES = auto()
    E_ARG_BOUND_VALUE_MULT_ERROR = auto()

    def __str__(self) -> str:
        return self.name


@dataclass
class CliDefValidationRecord:
    error: CliDefValidationError
    node: ResolvedCliDefNode

    def __str__(self) -> str:
        return f"({str(self.error), {self.node.defpath}})"


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
    def errors(self) -> Sequence[CliDefValidationError]:
        return [r.error for r in self._records]

    def clear_errors(self):
        self._records.clear()



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
                self._records.append(
                    CliDefValidationRecord(
                        CliDefValidationError.E_ARG_BOUND_VALUE_TYPE_ERROR,
                        arg
                    )
                )
            # 1.2) choices check
            if arg.choices:
                if bound_value not in arg.choices:
                    self._records.append(
                        CliDefValidationRecord(
                            CliDefValidationError.E_ARG_BOUND_VALUE_NOT_IN_CHOICES,
                            arg
                        )
                    )
            # 1.3) mult check
            if not self.accepts_value_mult(bound_value, arg.mult):
                self._records.append(
                    CliDefValidationRecord(
                        CliDefValidationError.E_ARG_BOUND_VALUE_MULT_ERROR,
                        arg
                    )
                )
        # 2) 


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
