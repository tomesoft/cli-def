# cli_def/runtime/context.py
from __future__ import annotations
from typing import Optional, Any
from dataclasses import dataclass, field

@dataclass
class CliRuntimeContext:
    debug: bool = False
    verbose: bool = False
    lang: str = "en"
    backend: Optional[str] = None # "argparse"  or "click"
    extra: dict[str, Any] = field(default_factory=dict)
