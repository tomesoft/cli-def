# main.py
from pathlib import Path
from cli_def.runtime import CliRunner
from cli_def.ops import load_cli_def_beside

cli_def = load_cli_def_beside(Path(__file__), "cli_def.toml")
runner = CliRunner(cli_def)

if __name__ == "__main__":
    runner.run()