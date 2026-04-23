# cli_def/test_support/test_runner.py
from __future__ import annotations
from typing import Any, Mapping, Tuple
import tomllib
from pathlib import Path
import logging

from ..basic.basic_types import PathLike
from ..core.models import (
    CliDef
)
from ..ops.loader import (
    load_cli_def_beside,
    load_cli_def_path,
)
from ..runtime import (
    CliRunner,
    CliEvent,
    CliResult,
)
from ..ops.utils.renderer import (
    Style,
)
from ..ops.utils.pretty_renderer import PrettyRenderer


class CliTestRunner:

    def __init__(self):
        self._test_file : Path|None = None
        self._target_cli_file: Path|None = None
        self.renderer = PrettyRenderer()

        # counters
        self.skipped = 0
        self.passed = 0
        self.failed = 0


    def load_tests(self, path: PathLike) -> Mapping[str, Any]|None:
        mapping = {}
        with open(path, "rb") as file:
            mapping = tomllib.load(file)
        if "cli_test" in mapping:
            self._test_file = Path(path)
            return mapping["cli_test"]
        return None


    def load_cli(self, path: PathLike) -> CliDef|None:
        # fullpath
        if str(path).startswith("/"):
            cli_def = load_cli_def_path(path)
            if cli_def:
                self._target_cli_file = Path(path)
            return cli_def

        # relative path
        assert self._test_file
        cli_def = load_cli_def_beside(self._test_file, path)
        if cli_def:
            base_dir = self._test_file.resolve().parent
            self._target_cli_file = Path(base_dir / path)
        return cli_def


    def run(self, path: PathLike):
        mapping = self.load_tests(path)
        if mapping is None:
            return

        if "target_cli" not in mapping:
            return

        target_cli_path = mapping["target_cli"]
        cli_def = self.load_cli(target_cli_path)
        if cli_def is None:
            print(f"could not load target cli: {target_cli_path}")
            return

        runner = CliRunner(
            cli_def,
            # dry_run_handler=self.dry_run_handler
        )

        tests: list[dict[str, Any]] = mapping["tests"]
        num_max_width = len(str(len(tests)))
        test_names = [test.get("name", f"test({i})") for i, test in enumerate(tests, start=1)]
        name_max_width = max(len(name) for name in test_names)

        print(f" {len(tests)} tests found.")
        for i, (name, test) in enumerate(zip(test_names, tests), start=1):

            dots = "." * (name_max_width - len(name) + 3)
            print(f"{str(i).rjust(num_max_width)}"
                  f" {name} {dots} ", end="")
            logging.info(f"{i} test name: {name}, command:{test["command"]!r}")

            # skip
            if test.get("skip", False):
                self.skipped += 1
                print(self.renderer.render_text("SKIP", Style(fg_color="yellow")))
                continue

            # run
            result, stdout, stderr = runner.run_and_capture(test["command"])

            # check
            self.check_result(test, result, stdout, stderr)

        self.format_summary()


    def check_result(self, test: Mapping[str, Any], result: CliResult, stdout: str, stderr: str):
        try:
            if "expect_stdout" in test:
                expect = test["expect_stdout"]
                self.check_stdout(expect, stdout)

            if "expect_stdout_contains" in test:
                expect = test["expect_stdout_contains"]
                self.check_stdout_contains(expect, stdout)

            if "expect_stderr" in test:
                expect = test["expect_stderr"]
                self.check_stderr(expect, stderr)

            if "expect_stderr_contains" in test:
                expect = test["expect_stderr_contains"]
                self.check_stderr_contains(expect, stderr)

            if "expect_exit_code" in test:
                expect = test["expect_exit_code"]
                self.check_exit_code(expect, result.exit_code)

            self.format_pass("PASS")
            self.passed += 1
        except AssertionError:
            self.failed += 1
        except Exception:
            pass


    def check_stdout_contains(self, expect: str, stdout: str):
        #stdout = stdout.rstrip("\n")
        logging.info(f"  expect:{expect!r}, stdout:{stdout!r}")
        try:
            assert expect in stdout
        except AssertionError as e:
            self.format_failed("FAILED")
            print(self.renderer.render_text("  [stdout] missing:", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    expected: {expect!r}", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    actual:   {stdout!r}", Style(fg_color="magenta")))
            raise e


    def check_stdout(self, expect: str, stdout: str):
        stdout = stdout.rstrip("\n")
        logging.info(f"  expect:{expect!r}, stdout:{stdout!r}")
        try:
            assert expect == stdout
        except AssertionError as e:
            self.format_failed("FAILED")
            print(self.renderer.render_text("  [stdout] mismatch:", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    expected: {expect!r}", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    actual:   {stdout!r}", Style(fg_color="magenta")))
            raise e


    def check_stderr_contains(self, expect: str, stderr: str):
        #stderr = stderr.rstrip("\n")
        logging.info(f"  expect:{expect!r}, stderr:{stderr!r}")
        try:
            assert expect in stderr
        except AssertionError as e:
            self.format_failed("FAILED")
            print(self.renderer.render_text("  [stderr] missing:", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    expected: {expect!r}", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    actual:   {stderr!r}", Style(fg_color="magenta")))
            raise e


    def check_stderr(self, expect: str, stderr: str):
        stderr = stderr.rstrip("\n")
        logging.info(f"  expect:{expect!r}, stderr:{stderr!r}")
        try:
            assert expect == stderr
        except AssertionError as e:
            self.format_failed("FAILED")
            print(self.renderer.render_text("  [stderr] mismatch:", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    expected: {expect!r}", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    actual:   {stderr!r}", Style(fg_color="magenta")))
            raise e


    def check_exit_code(self, expect: int, exit_code: int):
        logging.info(f"  expect:{expect!r}, exit_code:{exit_code!r}")
        try:
            assert expect == exit_code
        except AssertionError as e:
            self.format_failed("FAILED")
            print(self.renderer.render_text("  [exit_code] mismatch:", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    expected: {expect!r}", Style(fg_color="magenta")))
            print(self.renderer.render_text(f"    actual:   {exit_code!r}", Style(fg_color="magenta")))
            raise e


    def format_pass(self, message: str):
        print(self.renderer.render_text(message, Style(fg_color="green")))


    def format_failed(self, message: str):
        print(self.renderer.render_text(message, Style(fg_color="red")))


    def format_summary(self):
        summary = []
        if self.skipped:
            summary.append(self.renderer.render_text(
                f"{self.skipped} skipped, ", Style(fg_color="yellow")
            ))
        if self.failed:
            summary.append(self.renderer.render_text(
                f"{self.failed} failed, ", Style(fg_color="red")
            ))

        summary.append(self.renderer.render_text(
                f"{self.passed} passed", Style(fg_color="green")
        ))

        print()
        print("".join((str(s) for s in summary)))

    @staticmethod
    def dry_run_handler(event: CliEvent):
        print(f"  @@{event.params}")

