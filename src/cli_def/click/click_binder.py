# cli_def/click/click_binder.py
try:
    import click
except ImportError:
    raise ImportError(
        "click is required for click builder. Install with `cli-def[click]`"
    )
from typing import Any, Mapping

from ..runtime import (
    Dispatcher
)

class ClickBinder:

    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher

    def bind(self, root, mapping: Mapping[str, Any]):
        for defpath, obj in mapping.items():
            if isinstance(obj, click.Command):
                # subcommand を持つGroupは callback を設定しない
                if isinstance(obj, click.Group):
                    continue
                #print(f"@@@ try to override callback of {defpath}")
                obj.callback = self._make_callback(defpath)

    def _make_callback(self, defpath):
        def callback(**kwargs):
            #print(f"@@@ internal callback called: {defpath}")
            self.dispatcher._dispatch(defpath, kwargs)
        return callback