# cli_def/demo_handlers.py
from __future__ import annotations

from .runtime import CliEvent, HandlerResult

# --------------------------------------------------------------------------------
# handlers for beginner profile
# --------------------------------------------------------------------------------
def echo(event: CliEvent):
    msg = event.params.get("message", [])
    result = " ".join(msg)
    print(result)

    return HandlerResult.make_result(
        event,
        "message",
        data=result,
    )


def greet(event: CliEvent):
    name = event.params.get("name") or "world"
    text = f"Hello, {name}!"

    if event.params.get("upper"):
        text = text.upper()

    print(text)

    return HandlerResult.make_result(
        event,
        "greet",
        data=text,
    )


# --------------------------------------------------------------------------------
# handlers for advanced profile
# --------------------------------------------------------------------------------
def build(event: CliEvent):
    target = event.params["target"]
    verbose = event.params.get("verbose", False)

    text = f"[build] target={target} verbose={verbose}"
    print(text)

    return HandlerResult.make_result(
        event,
        "build",
        data=text,
    )


def test(event: CliEvent):
    pattern = event.params.get("pattern") or "all"
    verbose = event.params.get("verbose", False)

    text = f"[test] pattern={pattern} verbose={verbose}"
    print(text)

    return HandlerResult.make_result(
        event,
        "test",
        data=text,
    )


def deploy(event: CliEvent):
    env = event.params.get("env") or "dev"
    force = event.params.get("force", False)

    text = f"[deploy] env={env} force={force}"
    print(text)

    return HandlerResult.make_result(
        event,
        "deploy",
        data=text,
    )
