# cli_def/validator/init.py
# package marker

from .validator import (
    CliDefValidator,
    CliDefValidationError,
)

__all__ = [
    "CliDefValidator",
    "CliDefValidationError"
]