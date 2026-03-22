# cli_def/runtime/session.py
import shlex
from typing import Optional, Callable

from ..models import CliDef
from ..parsers import CliDefParser
from ..argparse import ArgparseBuilder
from .dispatcher import Dispatcher


class CliSession:
    def __init__(self, cli_def: CliDef, fallback_handler :Callable=None, profile: str=None):
        self.cli_def = cli_def
        self.fallback_handler = fallback_handler
        self.profile = profile

        self._build_runtime()

    # --- lifecycle -------------------------------------------------

    def _build_runtime(self):
        builder = ArgparseBuilder()
        self.parser = builder.build_argparse(
            self.cli_def,
            prog=self._make_prog_name()
        )
        self.dispatcher = Dispatcher(self.cli_def, self.fallback_handler)

    def _make_prog_name(self):
        if self.profile:
            return f"{self.cli_def.key}[{self.profile}]"
        return self.cli_def.key

    # --- public API ------------------------------------------------

    def reload_from_text(self, toml_text: str):
        parser = CliDefParser()
        self.cli_def = parser.parse_from_toml_text(toml_text)
        self._build_runtime()

    def reload_from_file(self, path: str):
        parser = CliDefParser()
        self.cli_def = parser.parse_from_toml(path)
        self._build_runtime()

    # --- execution -------------------------------------------------

    def execute_line(self, line: str):
        argv = shlex.split(line)
        args = self.parser.parse_args(argv)
        return self.dispatcher.dispatch(args)

    # --- REPL ------------------------------------------------------

    def repl(self, prompt: str = "cli-def> "):
        while True:
            try:
                line = input(prompt).strip()
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print("<Ctrl-C>")
                break

            if not line:
                continue

            try:
                if self._handle_builtin(line):
                    continue
            except EOFError:
                print()
                break

            try:
                self.execute_line(line)
            except Exception as e:
                print(f"[error] {e}")
            except SystemExit: # parse error
                print("Parse Error")
                continue

    # --- built-in commands -----------------------------------------

    def _handle_builtin(self, line: str) -> bool:
        if line in ("exit", "quit"):
            raise EOFError()

        if line == "help":
            self.parser.print_help()
            return True

        if line == "reload":
            # 直近の定義を再構築（必要なら拡張）
            self._build_runtime()
            print("[reloaded]")
            return True

        if line.startswith("load "):
            path = line.split(" ", 1)[1]
            self.reload_from_file(path)
            print(f"[loaded] {path}")
            return True

        return False