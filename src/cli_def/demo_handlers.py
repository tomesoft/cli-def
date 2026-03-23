# cli_def/demo_handlers.py

from .runtime import CliEvent

# --------------------------------------------------------------------------------
# handlers for beginner profile
# --------------------------------------------------------------------------------
def echo(event: CliEvent):
    msg = event.params.get("message", [])
    print(" ".join(msg))


def greet(event: CliEvent):
    name = event.params.get("name") or "world"
    text = f"Hello, {name}!"

    if event.params.get("upper"):
        text = text.upper()

    print(text)


# --------------------------------------------------------------------------------
# handlers for advanced profile
# --------------------------------------------------------------------------------
def build(event: CliEvent):
    target = event.params["target"]
    verbose = event.params.get("verbose", False)

    print(f"[build] target={target} verbose={verbose}")


def test(event: CliEvent):
    pattern = event.params.get("pattern") or "all"
    verbose = event.params.get("verbose", False)

    print(f"[test] pattern={pattern} verbose={verbose}")


def deploy(event: CliEvent):
    env = event.params.get("env") or "dev"
    force = event.params.get("force", False)

    print(f"[deploy] env={env} force={force}")