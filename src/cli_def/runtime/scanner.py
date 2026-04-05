# cli_def/runtime/scanner.py
from __future__ import annotations

from typing import Mapping, Any, Sequence
from dataclasses import dataclass, field

import pkgutil
import importlib
import importlib.util
import logging
import subprocess
import sys
import os
import json
import copy

from .handler_support import (
    CliHandlerMeta,
    get_all_handlers_catalog,
)

@dataclass
class CliHandlerScannerResult:
    scan_coverage: dict[str, Any]|None = None
    catalog: Mapping[str, Sequence[CliHandlerMeta]]|None = None
    _catalog_digest: dict[str, Sequence[Any]]|None = None

    def to_digest(self) -> dict[str, Any]:
        if self._catalog_digest is None:
            digest = {}
            if self.catalog:
                for key, lst in self.catalog.items():
                    digest[key] = [meta.to_dict() for meta in lst]
            self._catalog_digest = digest

        return {
            "scan_coverage": self.scan_coverage,
            "catalog_digest": self._catalog_digest
        }

    @classmethod
    def from_digest(cls, digest: Mapping[str, Any]) -> CliHandlerScannerResult:
        return cls(
            scan_coverage = digest.get("scan_coverage"),
            catalog = None,
            _catalog_digest = digest.get("catalog_digest")
        )



class CliHandlerScanner:

    def scan(self,
            package_name: str,
            *,
            no_subprocess: bool,
            recursive: bool,
    ) -> CliHandlerScannerResult|None:

        #print(f"package_name: {package_name}")
        if not self.can_import(package_name):
            print(f"[ERROR] package not found: {package_name}")
            return None

        if no_subprocess:
            logging.info("[scan without subprocess]")
            scan_coverage = self.import_modules(package_name, recursive)
            catalog = get_all_handlers_catalog()
            return CliHandlerScannerResult(
                scan_coverage=dict(scan_coverage),
                catalog=catalog
            )

        # use subprocess
        logging.info("[scan with subprocess]")
        proc_result = subprocess.run([
            sys.executable,
            "-m",
            "cli_def.runtime._internal.scan_runner",
            package_name,
            ] + (
                ["--recursive"] if recursive else []
            )
            , capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        if proc_result.returncode != 0:
            logging.warning("scanner subprocess unsucceeded")
            return None

        logging.debug(f"@@@ result.stdout: {proc_result.stdout}")
        digest = json.loads(proc_result.stdout)

        if not isinstance(digest, Mapping):
            logging.warning("scanner subprocess returns incorrect format of value")
            return None

        return CliHandlerScannerResult.from_digest(digest)



    def can_import(self, module_name: str) -> bool:
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except ModuleNotFoundError:
            return False


    def import_modules(self, package: str, recursive: bool) -> Mapping[str, bool]:
        result = {}
        pkg_or_module = None
        try:
            pkg_or_module = importlib.import_module(package)
            result[package] = True
        except ImportError:
            result[package] = False

        logging.debug(f"@import_modules() type({package}) = {type(pkg_or_module)}")

        if pkg_or_module and hasattr(pkg_or_module, "__path__"):
            pkg = pkg_or_module

            if not recursive:
                for _, name, ispkg in pkgutil.iter_modules(pkg.__path__):
                    pkg = f"{package}.{name}"
                    try:
                        importlib.import_module(f"{package}.{name}")
                        result[pkg] = True
                    except ImportError:
                        result[pkg] = False
            else:
                for _, name, _ in pkgutil.walk_packages(pkg.__path__, package + "."):
                    try:
                        importlib.import_module(name)
                        result[name] = True
                    except ImportError:
                        result[name] = False
        return result



