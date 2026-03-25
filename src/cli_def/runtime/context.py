# cli_def/runtime/context.py
from dataclasses import dataclass

@dataclass
class CliRuntimeContext:
    debug: bool = False
    verbose: bool = False
    lang: str = "en"
