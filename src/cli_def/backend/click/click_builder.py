# cli_def/backend/click/click_builder.py
from typing import Any, Mapping, Iterable, Sequence
try:
    import click
except ImportError:
    raise ImportError(
        "click is required for click builder. Install with `cli-def[click]`"
    )

from ...core.models import (
    ResolvedCliDefNode,
    ResolvedCliDef,
    ResolvedCommandDef,
    ResolvedExecutableNode,
    ResolvedArgumentDef,
    MultDef
)

from typing import Union

ClickObject = Union[
    click.Group,
    click.Command,
    click.Option,
]

GroupOrCommand = Union[
    click.Group,
    click.Command,
]

from ..protocols import BuilderProtocol


class ClickBuilder(BuilderProtocol):

    def __init__(self):
        self._defpath_mapping: dict[str, ClickObject] = {}


    @property
    def defpath_mapping(self) -> Mapping[str, ClickObject]:
        return self._defpath_mapping


    def build(self, cliDef: ResolvedCliDef) -> GroupOrCommand:
        return self.build_click(cliDef)


    def _register(self, node, obj):
        self._defpath_mapping[node.defpath] = obj


    def build_click(self, cliDef: ResolvedCliDef) -> GroupOrCommand:
        if not cliDef.commands:
            return self._build_root_command(cliDef)

        return self._build_root_group(cliDef)


    def _build_root_command(self, cliDef: ResolvedCliDef) -> click.Command:
        params = [self._build_param(arg) for arg in cliDef.arguments]

        def callback(**kwargs):
            click.echo(f"{cliDef.defpath} {kwargs}")

        cmd = click.Command(
            name=cliDef.key,
            help=cliDef.help,
            params=params,
            callback=callback,
            context_settings={
                "ignore_unknown_options": True,
                "allow_extra_args": True,
            }
        )

        self._register(cliDef, cmd)

        return cmd


    def _build_root_group(self, cliDef: ResolvedCliDef) -> click.Group:
        root = click.Group(name=cliDef.key, help=cliDef.help)

        self._register(cliDef, root)

        self._attach_params(root, cliDef.arguments)

        if cliDef.commands:
            self._attach_commands(root, cliDef.commands)

        return root


    def _build_command(self, cmdDef: ResolvedCommandDef) -> click.Command:
        params = [
            self._build_param(arg)
            for arg in cmdDef.arguments
            if not arg.has_bound_value
        ]

        if cmdDef.subcommands:
            grp = click.Group(name=cmdDef.key, help=cmdDef.help, params=params)

            self._register(cmdDef, grp)

            for sub in cmdDef.subcommands:
                grp.add_command(self._build_command(sub))

            return grp

        # leaf command
        def callback(**kwargs):
            click.echo(f"{cmdDef.defpath} {kwargs}")

        cmd = click.Command(
            name=cmdDef.key,
            help=cmdDef.help,
            params=params,
            callback=callback,
            context_settings={
                "ignore_unknown_options": True,
                "allow_extra_args": True,
            }
        )

        self._register(cmdDef, cmd)

        return cmd


    def _build_param(self, arg: ResolvedArgumentDef) -> click.Parameter:
        if arg.option:
            # option
            param = click.Option(
                [arg.option] + (list(arg.aliases) or []),
                help=arg.help,
                default=arg.default,
                is_flag=arg.is_flag or False,
            )
            param.name = arg.key
            self.apply_mult(param, arg.mult)
        else:
            # positional
            kwargs = self.to_kwargs_for_positional(arg.mult)
            param = click.Argument(
                param_decls=[arg.key],
                **kwargs
            )

        self._register(arg, param)

        return param


    def _attach_commands(
            self,
            parent: click.Group,
            commands: Iterable[ResolvedCommandDef]
        ):
        for cmd in commands or []:
            parent.add_command(self._build_command(cmd))


    def _attach_params(
            self,
            cmd: click.Command,
            arguments: Iterable[ResolvedArgumentDef]
        ):
        for arg in arguments or []:
            if arg.has_bound_value:
                continue
            cmd.params.append(self._build_param(arg))


    def apply_mult(self, param: click.Parameter, mult: MultDef):
        if mult.is_fixed:
            param.nargs = mult.lower
        elif mult.is_unbounded:
            param.multiple = True
        elif mult.is_optional:
            param.nargs = 1

    def to_kwargs_for_positional(self, mult: MultDef) -> dict[str, Any]:
        if mult.is_fixed:
            return {"nargs": mult.lower, "required": True}
        elif mult.is_optional:
            return {"nargs": 1, "required": False}
        elif mult.is_unbounded:
            return {"nargs": -1, "required": mult.lower != 0}
        return {"nargs": 1} # TODO
