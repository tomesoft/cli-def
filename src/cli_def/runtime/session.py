# cli_def/runtime/session.py
import shlex
from typing import Optional, Callable

from ..models import CliDef
from ..parsers import CliDefParser
from ..argparse import ArgparseBuilder
from .dispatcher import Dispatcher


# --------------------------------------------------------------------------------
# CliSession class
# --------------------------------------------------------------------------------
class CliSession:

    def __init__(
            self,
            cli_def: CliDef,
            fallback_handler :Callable=None,
            profile: str=None,
            cli_def_file: str=None,
            ):
        self.cli_def = cli_def
        self.fallback_handler = fallback_handler
        self.profile = profile
        self._cli_def_file = cli_def_file

        self._build_runtime()

    # --- lifecycle -------------------------------------------------

    def _build_runtime(self):
        builder = ArgparseBuilder()
        self.parser = builder.build_argparse(
            self.cli_def,
            prog=self._make_prog_name()
        )
        self.dispatcher = Dispatcher(self.cli_def, self.fallback_handler)

    def _make_prog_name(self) -> str:
        if self.profile:
            return f"{self.cli_def.key}[{self.profile}]"
        return self.cli_def.key

    # --- public API ------------------------------------------------

    def reload_from_text(self, toml_text: str) -> bool:
        parser = CliDefParser()
        self.cli_def = parser.parse_from_toml_text(toml_text)
        self._build_runtime()
        return True

    def reload_from_file(self, path: str=None) -> bool:
        path = path or self._cli_def_file
        if path is None:
            return False
        parser = CliDefParser()
        self.cli_def = parser.parse_from_toml(path)
        self._build_runtime()
        if path != self._cli_def_file:
            self._cli_def_file = path
        return True

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
            if self.reload_from_file():
                print("[reloaded]")
            return True

        if line.startswith("load "):
            path = line.split(" ", 1)[1]
            if self.reload_from_file(path):
                print(f"[loaded] {path}")
            return True

        return False