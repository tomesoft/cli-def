# cli_def/core/models/common/mult_def.py
from __future__ import annotations
from typing import Any, Mapping, Tuple, Sequence
from dataclasses import dataclass
import re



# for multiplicty normalization
@dataclass
class MultDef:
    lower: int
    upper: int | None


    @property
    def is_fixed(self) -> bool:
        return self.upper is not None and self.lower == self.upper

    @property
    def is_unbounded(self) -> bool:
        return self.upper is None

    @property
    def is_optional(self) -> bool:
        return self.lower == 0 and self.upper == 1


    @classmethod
    def from_any(cls, val: Any) -> MultDef:
        if isinstance(val, MultDef):
            return MultDef(val.lower, val.upper)
        if isinstance(val, str):
            return cls.from_str(val)
        if isinstance(val, int):
            return MultDef(val, val)
        if isinstance(val, tuple):
            return cls.from_tuple(val)
        if isinstance(val, Sequence):
            return cls.from_sequence(val)
        if isinstance(val, Mapping):
            return cls.from_mapping(val)

        raise ValueError(f"Invalid mult spec: {val!r}")


    @classmethod
    def from_str(cls, text: str) -> MultDef:
        text = text.strip()

        # 記号系
        if text in ("?",):
            return cls(0, 1)
        if text in ("*",):
            return cls(0, None)
        if text in ("+",):
            return cls(1, None)

        # 数値（固定長）
        if text.isdigit():
            n = int(text)
            return cls(n, n)

        # 範囲系 ("0..*"も許容)
        m = re.fullmatch(r"(\d+)\.\.((\d+)|\*)", text)
        if m:
            lower = int(m.group(1))
            upper = m.group(2)
            upper =  None if upper == "*" else int(upper)

            if upper is not None and lower > upper:
                raise ValueError(f"Invalid range: {text}")

            return cls(lower, upper)

        raise ValueError(f"Invalid mult spec: {text}")

            
    def to_str(self, *, span: bool=False) -> str:
        lower_str = str(self.lower)
        if not span:
            if self.is_fixed:
                return lower_str

            if self.is_optional:
                return "?"

            if self.is_unbounded:
                if self.lower == 0:
                    return "*"
                elif self.lower == 1:
                    return "+"

        upper_str = "*" if self.upper is None else str(self.upper)
        
        return f"{lower_str}..{upper_str}"


    def to_tuple(self) -> Tuple[int, int|None]:
        return (self.lower, self.upper)

    @classmethod
    def from_tuple(cls, val_pair: Tuple[int, int|None]) -> MultDef:
        lower, upper = val_pair
        return MultDef(
            cls.eval_as_lower(lower),
            cls.eval_as_upper(upper),
        )

    def to_dict(self) -> dict[str, int|None]:
        return {
            "lower": self.lower,
            "upper": self.upper
        }
    
    @classmethod
    def from_mapping(cls, mapping: Mapping[str, int|None]) -> MultDef:
        if "lower" not in mapping or "upper" not in mapping:
            raise ValueError(f"Invalid mult spec: {mapping!r}")
        
        lower = mapping["lower"]
        upper = mapping["upper"]

        return MultDef(
            cls.eval_as_lower(lower),
            cls.eval_as_upper(upper),
        )

    def to_sequence(self) -> Sequence[int|None]:
        return [self.lower, self.upper]


    @classmethod
    def from_sequence(cls, seq: Sequence[int|None]) -> MultDef:
        if len(seq) == 0 or len(seq) > 2:
            raise ValueError(f"Invalid mult spec: {seq!r}")
        
        if len(seq) == 1:
            val = seq[0]
            return MultDef(
                cls.eval_as_lower(val),
                cls.eval_as_upper(val),
            )
        
        lower, upper = seq[0], seq[1]

        return MultDef(
            cls.eval_as_lower(lower),
            cls.eval_as_upper(upper),
        )


    @classmethod
    def eval_as_lower(cls, val: Any) -> int:
        if val is None:
            return 0
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            return int(val)
        if val == "*":
            return 0
        if val == "+":
            return 1
        if str(val).isdigit():
            return int(val)

        raise ValueError(f"Invalid mult spec: {val!r}")
        
    @classmethod
    def eval_as_upper(cls, val: Any) -> int|None:
        if val is None:
            return None
        if isinstance(val, int):
            return val
        if val == "*":
            return None
        if val == "+":
            return None
        if str(val).isdigit():
            return int(val)

        raise ValueError(f"Invalid mult spec: {val!r}")