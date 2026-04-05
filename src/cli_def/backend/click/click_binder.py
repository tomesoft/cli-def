# cli_def/backend/click/click_binder.py
from typing import Any, Mapping
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

from ..protocols import BinderProtocol


class ClickBinder(BinderProtocol):

    def __init__(
            self,
            dispatcher: CliDispatcher,
            ctx: CliRuntimeContext|None = None
        ):
        self.dispatcher = dispatcher
        self.runtime_ctx = ctx


    def bind(self, defpath_mapping: Mapping[str, object]):
        for defpath, obj in defpath_mapping.items():
            if isinstance(obj, click.Command):
                # subcommand を持つGroupは callback を設定しない
                if isinstance(obj, click.Group):
                    continue
                #print(f"@@@ try to override callback of {defpath}")
                obj.callback = self._make_callback(defpath)


    def _make_callback(self, defpath: str):
        @click.pass_context
        def callback(ctx, **kwargs):
            logging.info(f"@@@ internal callback called: {defpath} passthrough={ctx.args}")
            return self.dispatcher._dispatch(defpath, kwargs, extra_args=list(ctx.args), ctx=self.runtime_ctx)
        return callback