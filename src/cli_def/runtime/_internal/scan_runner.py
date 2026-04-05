# cli_def/runtime/_internal/scan_runner.py
from __future__ import annotations
import sys
import json

from ..scanner import CliHandlerScanner

# --------------------------------------------------------------------------------
# scanner support prog exected with subprocess
# --------------------------------------------------------------------------------
def main():
    package = sys.argv[1]
    recursive = "--recursive" in sys.argv

    scanner = CliHandlerScanner()
    result = scanner.scan(
        package,
        no_subprocess=True,
        recursive=recursive,
        )
    if result:
        digest = result.to_digest()
        print(json.dumps(digest))
    return 0


if __name__ == "__main__":
    main()