# cli_def/test_support/test_generator.py
from __future__ import annotations
from typing import Any, Mapping, Tuple

from ..basic.basic_types import PathLike
from ..core.models import (
    CliDef,
    ResolvedCliDefNode,
    ResolvedArgumentDef,
    ResolvedCommandDef,
    ResolvedCliDef,
)
from ..core.resolver import CliDefResolver
from ..ops.loader import load_cli_def_path
from ..runtime import CliRunner

class CliTestGenerator:

    def generate_from(
            self,
            cli_def_file: PathLike,
            *,
            with_output: bool = False,
        ) -> list[str]|None:

        cli_def = load_cli_def_path(cli_def_file)
        if cli_def is None:
            return None

        resolver = CliDefResolver()
        resolved = resolver.resolve(cli_def)

        lines: list[str] = []

        for node in resolved.iter_all_nodes():
            if isinstance(node, ResolvedCliDef):
                lines.append('[cli_test]')
                lines.append(f"# {node.key} tests")
                lines.append(f'target_cli = "{str(cli_def_file)}"')
                lines.append("")
            elif isinstance(node, ResolvedCommandDef):
                if not node.is_leaf:
                    continue

                lines.append('[[cli_test.tests]]')
                lines.append(f'name = "{node.key} test"')
                lines.append('command = [')
                for cmd_seq in node.get_command_sequence()[1:]:
                    lines.append(f'  "{cmd_seq}",')
                for arg in node.arguments:
                    if arg.has_bound_value:
                        continue
                    if arg.is_positional:
                        lines.append(f'  "<{arg.key}>",')
                    else:
                        lines.append(f'#  "{arg.option}",')
                lines.append(']')
                lines.append('expect_stdout = "SOMETHING"')
                lines.append("expect_exit_code = 0")
                lines.append("")

        return lines

