# cli_def/models/mult_def.py
from typing import Optional, Any, Iterator, Mapping, Tuple
from dataclasses import dataclass, field
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
    def from_str(cls, text: str) -> "MultDef":
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

            
    def to_str(self) -> str:
        if self.is_fixed:
            return str(self.lower)

        if self.is_optional:
            return "?"

        if self.is_unbounded:
            if self.lower == 0:
                return "*"
            elif self.lower == 1:
                return "+"

        lower_str = str(self.lower)
        upper_str = "*" if self.upper is None else str(self.upper)
        
        return f"{lower_str}..{upper_str}"


    def to_tuple(self) -> Tuple[int, int|None]:
        return (self.lower, self.upper)