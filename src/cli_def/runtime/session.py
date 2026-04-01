# cli_def/runtime/session.py
from __future__ import annotations
from typing import Optional, Callable, Any, Protocol
from dataclasses import dataclass

import logging
import pprint
try:
    import readline
except ImportError:
    pass

from ..models import CliDef
from ..parsers import CliDefParser
from .runner import CliRunner
from .context import CliRuntimeContext
from .result import ResultStore, ResultView, HandlerResult
from .event import CliEvent

# --------------------------------------------------------------------------------
# CliSession protocol
# --------------------------------------------------------------------------------
class CliSessionProtocol(Protocol):
    def repl(self):
        ...

    def push_repl_mode(self, name: str, mode_handler: Callable[[CliSessionProtocol, str], bool], prompt: str):
        ...

    def pop_repl_mode(self) -> bool:
        ...

    def get_result_store(self) -> ResultStore:
        ...


# --------------------------------------------------------------------------------
# Misc dataclasses
# --------------------------------------------------------------------------------
@dataclass
class ReplModeRecord:
    name: str
    mode_handler: Callable[[CliSession, str], bool]
    prompt: str|None


# --------------------------------------------------------------------------------
# CliSession class
# --------------------------------------------------------------------------------
class CliSession(CliSessionProtocol):
    _DEFAULT_PROMPT="cli-def> "

    SAFE_BUILTINS = {
        "len": len,
        "sorted": sorted,
        "min": min,
        "max": max,
        "sum": sum,
    }

    SAFE_GLOBALS = {
        "__builtins__": SAFE_BUILTINS
    }


    def __init__(
            self,
            cli_def: CliDef,
            fallback_handler: Callable[[CliEvent], HandlerResult|None]|None = None,
            profile: str|None = None,
            cli_def_file: str|None = None,
            *,
            ctx: CliRuntimeContext|None = None,
            ):
        self.cli_def: CliDef = cli_def
        self.fallback_handler: Callable[[CliEvent], HandlerResult|None]|None = fallback_handler
        self.profile = profile
        self._cli_def_file = cli_def_file
        self.runtime_ctx = ctx

        self.result_store = ResultStore()

        # self._prompt_stack: list[str] = []
        # self._repl_stack: list[Callable[[str], Any]] = []
        self._mode_stack: list[ReplModeRecord] = []

        self._build_runtime()

    # --- lifecycle -------------------------------------------------

    def _build_runtime(self):
        self.runner = CliRunner(
            self.cli_def,
            fallback_handler=self.fallback_handler,
            session=self,
        )

    def _make_prog_name(self) -> str:
        if self.profile:
            return f"{self.cli_def.key}[{self.profile}]"
        return self.cli_def.key

    # --- public API ------------------------------------------------

    def reload_from_text(self, toml_text: str) -> bool:
        parser = CliDefParser()
        new_cli_def = parser.parse_from_toml_text(toml_text)
        if new_cli_def is None:
            return False
        self.cli_def = new_cli_def
        self._build_runtime()
        return True

    def reload_from_file(self, path: str|None=None) -> bool:
        path = path or self._cli_def_file
        if path is None:
            return False
        parser = CliDefParser()
        new_cli_def = parser.parse_from_toml(path)
        if new_cli_def is None:
            return False
        self.cli_def = new_cli_def
        self._build_runtime()
        if path != self._cli_def_file:
            self._cli_def_file = path
        return True

    def get_result_store(self) -> ResultStore:
        return self.result_store

    # --- execution -------------------------------------------------

    def execute_line(self, line: str) -> Any:
        return self.runner.run(line)

    # --- REPL ------------------------------------------------------
    def push_repl_mode(
            self,
            name:str,
            mode_handler: Callable[[CliSession, str], bool],
            prompt: str|None = None):
        self._mode_stack.append(
            ReplModeRecord(
                name=name,
                mode_handler=mode_handler,
                prompt=prompt,
            )
        )


    def pop_repl_mode(self):
        if len(self._mode_stack):
            self._mode_stack.pop()
            return True
        return False


    def _setup_initial_prompt(self, prompt: str|None):
        prompt = prompt or self.cli_def.prompt or self._DEFAULT_PROMPT
        self._initial_prompt = prompt


    def _make_prompt(self):
        return "".join(
            [self._initial_prompt.strip()] +
            [(mode.prompt or mode.name).strip()
              for mode in self._mode_stack]
            ) + " "


    def repl(self, prompt: str|None = None):
        self._setup_initial_prompt(prompt)
        while True:
            prompt = self._make_prompt()
            try:
                line = input(prompt).strip()
            except EOFError:
                print()
                if not self.pop_repl_mode():
                    break
            except KeyboardInterrupt:
                print("<Ctrl-C>")
                if not self.pop_repl_mode():
                    break

            if len(self._mode_stack):
                self._mode_stack[-1].mode_handler(self, line)
                continue

            if not line:
                continue

            try:
                if self._handle_builtin(line):
                    continue
            except EOFError:
                print()
                break

            try:
                before_result_len = self.result_store.len()
                self.execute_line(line)
                after_result_len = self.result_store.len()
                if after_result_len != before_result_len:
                    print()
                    print(f"-> out[{after_result_len-1}]")
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
            # self.parser.print_help()
            self.runner.show_help()
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

        if line == ">":
            self.push_repl_mode(
                "eval",
                lambda _, x: self._eval_mode(x),
                "eval>> "
            )
            return True

        if line.startswith(">"):
            possible_expr = line[1:].strip()
            logging.debug(f"@@@ possible_expr={possible_expr!r}")
            try:
                evaluated = self._repl_eval_expression(possible_expr)
                pprint.pprint(evaluated)
            except Exception as e:
                print(f"Error: {type(e).__name__}: {e}")
            return True

        return False


    # --- eval mode  ------------------------------------------------------

    def _eval_mode(self, line: str):
        possible_expr = line.strip()
        if len(line) == 0:
            self.pop_repl_mode()
            return True

        logging.debug(f"@@@ possible_expr={possible_expr!r}")
        try:
            evaluated = self._repl_eval_expression(possible_expr)
            pprint.pprint(evaluated)
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
        return True


    def _repl_eval_expression(self, expr):
        out_views = [ResultView(r) for r in self.result_store.all()]
        last_out_view = out_views[-1] if len(out_views) else None
        context = {
            "raw_out": self.result_store.all_data(),
            "out": out_views,
            "_": last_out_view,
        }

        return eval(expr, self.SAFE_GLOBALS, context)
