# handlers.py
from cli_def.runtime import CliEvent

def hello(event: CliEvent):
    name = event.params.get("name") or "world"
    print(f"Hello, {name}!")