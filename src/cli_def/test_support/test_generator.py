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
    ResolvedExecutableNode,
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
                lines.extend(
                    self._generate_executable(node)
                )

            elif isinstance(node, ResolvedCommandDef):
                if not node.is_leaf:
                    continue
                lines.extend(
                    self._generate_executable(node)
                )


        return lines

    def _generate_executable(self, node: ResolvedExecutableNode) -> list[str]:
        lines: list[str] = []
        if not node.is_leaf:
           return lines

        lines.append('[[cli_test.tests]]')
        lines.append(f'name = "{node.key} test"')
        lines.append('command = [')

        if isinstance(node, ResolvedCommandDef):
            for cmd_seq in node.get_command_sequence()[1:]:
                lines.append(f'  "{cmd_seq}",')
        for arg in node.arguments:
            if arg.has_bound_value:
                continue
            if arg.is_positional:
                lines.append(f'  "<{arg.type}>", # {arg.key}')
            else:
                if arg.is_flag:
                    lines.append(f'#  "{arg.option}", # {arg.key}')
                elif arg.choices:
                    lines.append(f'#  "{arg.option}", "<{arg.type}>", # {arg.key}:{arg.choices!r}')
                else:
                    lines.append(f'#  "{arg.option}", "<{arg.type}>", # {arg.key}')
        lines.append(']')
        lines.append('expect_stdout = "SOMETHING"')
        lines.append("expect_exit_code = 0")
        lines.append("")

        return lines