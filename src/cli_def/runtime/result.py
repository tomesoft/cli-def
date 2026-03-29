# cli_def/runtime/result.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

from .event import CliEvent


@dataclass
class CliResult:
    results: list[HandlerResult]
    exit_code: int = 0


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
    def make_result(cls, event: CliEvent, message: str = None, data: Any = None) -> "HandlerResult":
        return cls(
            defpath=event.command.defpath,
            kind=ResultKind.OK,
            data=data,
            message=message
        )

    @classmethod
    def make_error(cls, event: CliEvent, message: str = None, data: Any = None) -> "HandlerResult":
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
        # if hasattr(data, "__len__"):
        #     return len(data)
        return len(data)


# # view object used in repl
# # smart unboxing in case of len(results) == 1
# class ResultListView:
#     def __init__(self, results):
#         print(f"@@@ ResultListView({type(results)})")
#         self._results = results

#     def _unboxed(self):
#         if len(self._results) == 1:
#             return self._results[0]
#         return None

#     def __getitem__(self, key):
#         unboxed = self._unboxed()
#         if unboxed is not None:
#             return unboxed.data[key]
#         return self._results[key]

#     def __getattr__(self, name):
#         unboxed = self._unboxed()
#         if unboxed is not None:
#             return getattr(unboxed.data, name)
#         raise AttributeError(name)

#     def __repr__(self):
#         unboxed = self._unboxed()
#         if unboxed is not None:
#             return repr(unboxed.data)
#         return repr(self._results)