# cli_def/demo/handlers.py
from __future__ import annotations

from pathlib import Path

from cli_def.runtime import (
    CliSession,
    CliEvent,
    CliHandlerResult,
    cli_def_handler,
)
from cli_def.ops import (
    load_cli_def_beside,
)
from cli_def.ops.dumper import CliDefDumper

# --------------------------------------------------------------------------------
# demo handler
# load profiles and go repl
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/demo", late_binding=True, description="builtin demo command handler")
def run_demo(event: CliEvent):
    profile = event.params.get("profile") or "beginner"

    cli_def = load_cli_def_beside(Path(__file__) , "profiles", profile + ".toml")

    if cli_def is None:
        msg = f"demo profile could not load: {profile}"
        print(msg)
        return CliHandlerResult.make_error(event, msg)

    CliDefDumper.dump_pretty(cli_def, as_help=True)

    print(f"=== demo: {profile} ===")
    print("Type 'help' to list commands, 'exit' to exit")

    # go repl 
    session = CliSession(
        cli_def,
        profile=profile,
        ctx=event.ctx,
    )
    session.repl(prompt=f"demo[{profile}]> ")

    return CliHandlerResult.make_result(
        event,
        "run_repl",
        data=session.result_store.all_data()
    )


# --------------------------------------------------------------------------------
# handlers for commands in beginner profile
# --------------------------------------------------------------------------------
def echo(event: CliEvent) -> CliHandlerResult:
    msg = event.params.get("message", [])
    result = " ".join(msg)
    print(result)

    return CliHandlerResult.make_result(
        event,
        "message",
        data=result,
    )


def greet(event: CliEvent) -> CliHandlerResult:
    name = event.params.get("name") or "world"
    text = f"Hello, {name}!"

    if event.params.get("upper"):
        text = text.upper()

    print(text)

    return CliHandlerResult.make_result(
        event,
        "greet",
        data=text,
    )


# --------------------------------------------------------------------------------
# handlers for commands in advanced profile
# --------------------------------------------------------------------------------
def build(event: CliEvent) -> CliHandlerResult:
    target = event.params["target"]
    verbose = event.params.get("verbose", False)

    text = f"[build] target={target} verbose={verbose}"
    print(text)

    return CliHandlerResult.make_result(
        event,
        "build",
        data=text,
    )


def test(event: CliEvent) -> CliHandlerResult:
    pattern = event.params.get("pattern") or "all"
    verbose = event.params.get("verbose", False)

    text = f"[test] pattern={pattern} verbose={verbose}"
    print(text)

    return CliHandlerResult.make_result(
        event,
        "test",
        data=text,
    )


def deploy(event: CliEvent) -> CliHandlerResult:
    env = event.params.get("env") or "dev"
    force = event.params.get("force", False)

    text = f"[deploy] env={env} force={force}"
    print(text)

    return CliHandlerResult.make_result(
        event,
        "deploy",
        data=text,
    )
