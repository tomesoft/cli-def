# cli_def/_internal/scan_runner.py
from typing import Any
import sys
import json

from ..runtime.handlers import (
    clear_all_handlers_catalog,
    clear_registry,
    scan_handlers,
    make_digest_scan_result,
    HandlerMeta,
)

def main():
    package = sys.argv[1]
    show_all = "--all" in sys.argv
    recursive = "--recursive" in sys.argv


    #clear_all_handlers_catalog()
    result: dict[str, Any] = scan_handlers(package, recursive=recursive)

    digest = make_digest_scan_result(result)

    print(json.dumps(digest))

    # for key, lst in catalog.items():
    #     print(f"{key}:")
    #     indent = "    "
    #     for meta in lst:
    #         if not show_all and not meta.late_bindings:
    #             continue
    #         print(indent + f"{meta.entrypoint}, desc={meta.description!r}, late_bindings={meta.late_bindings}, ")

if __name__ == "__main__":
    main()