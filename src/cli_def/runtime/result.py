# cli_def/runtime/result.py
from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

from .event import CliEvent


@dataclass
class CliResult:
    results: list[HandlerResult]
    exit_code: int = 0

    def all_data(self) -> list[Any]:
        return [
            r.to_dict() if r else None
            for r in self.results
        ]


class ResultKind(Enum):
    OK = auto()
    FAILED = auto()

    def __str__(self) -> str:
        return self.name


@dataclass
class HandlerResult:
    defpath: str
    kind: ResultKind = ResultKind.OK
    data: Any = None
    message: Optional[str] = None

    @classmethod
    def make_result(cls, event: CliEvent, message: str|None = None, data: Any = None, kind: ResultKind = ResultKind.OK) -> "HandlerResult":
        return cls(
            defpath=event.command.defpath,
            kind=kind,
            data=data,
            message=message
        )

    @classmethod
    def make_error(cls, event: CliEvent, message: str|None = None, data: Any = None) -> "HandlerResult":
        return cls(
            defpath=event.command.defpath,
            kind=ResultKind.FAILED,
            data=data,
            message=message
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "defpath": self.defpath,
            "kind": str(self.kind),
            "data": self.data,
            "message": self.message,
        }


class ResultStore:
    def __init__(self):
        self._results: list[HandlerResult] = []

    def add(self, result):
        self._results.append(result)

    def last(self):
        return self._results[-1] if self._results else None

    def get(self, index):
        return self._results[index]

    def all(self):
        return list(self._results)

    def len(self) -> int:
        return len(self._results)

    def all_data(self) -> list[Any]:
        return [
            r.to_dict() for r in self._results
        ]



# view object used in repl
class ResultView:
    def __init__(self, result: HandlerResult):
        self._r = result

    def __getitem__(self, key):
        return self._r.data[key]

    def __repr__(self):
        return repr(self._r.data)

    def __len__(self):
        data = self._r.data
        return len(data)

    def __bool__(self):
        data = self._r.data
        return bool(data)

    def __iter__(self):
        data = self._r.data
        return iter(data)

    def __contains__(self, item):
        data = self._r.data
        return item in data

