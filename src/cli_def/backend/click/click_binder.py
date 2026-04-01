# cli_def/backend/click/click_binder.py
from typing import Any, Mapping, Optional
import logging

try:
    import click
except ImportError:
    raise ImportError(
        "click is required for click builder. Install with `cli-def[click]`"
    )

from ...runtime import (
    CliDispatcher,
    CliRuntimeContext,
)

class ClickBinder:

    def __init__(self, dispatcher: CliDispatcher, ctx: Optional[CliRuntimeContext] = None):
        self.dispatcher = dispatcher
        self.runtime_ctx = ctx

    def bind(self, root, mapping: Mapping[str, Any]):
        for defpath, obj in mapping.items():
            if isinstance(obj, click.Command):
                # subcommand を持つGroupは callback を設定しない
                if isinstance(obj, click.Group):
                    continue
                #print(f"@@@ try to override callback of {defpath}")
                obj.callback = self._make_callback(defpath)

    def _make_callback(self, defpath):
        @click.pass_context
        def callback(ctx, **kwargs):
            logging.info(f"@@@ internal callback called: {defpath} passthrough={ctx.args}")
            return self.dispatcher._dispatch(defpath, kwargs, extra_args=list(ctx.args), ctx=self.runtime_ctx)
        return callback