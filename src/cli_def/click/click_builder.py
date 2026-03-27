# cli_def/click/click_builder.py
try:
    import click
except ImportError:
    raise ImportError(
        "click is required for click builder. Install with `cli-def[click]`"
    )
from typing import Any, Mapping, Iterable

from ..models import (
    CliDefNode,
    CliDef,
    CommandDef,
    ArgumentDef,
    MultDef
)

from typing import Union

ClickObject = Union[
    click.Group,
    click.Command,
    click.Option,
]

class ClickBuilder:

    def __init__(self):
        self._defpath_mapping: dict[str, ClickObject] = {}

    @property
    def defpath_mapping(self) -> Mapping[str, ClickObject]:
        return self._defpath_mapping

    def _register(self, node, obj):
        self._defpath_mapping[node.defpath] = obj


    def build_click(self, cliDef: CliDef) -> click.Group | click.Command:

        if not cliDef.commands:
            return self._build_root_command(cliDef)

        return self._build_root_group(cliDef)


    def _build_root_command(self, cliDef: CliDef):

        params = [self._build_param(arg) for arg in cliDef.arguments]

        def callback(**kwargs):
            click.echo(f"{cliDef.defpath} {kwargs}")

        cmd = click.Command(
            name=cliDef.key,
            help=cliDef.help,
            params=params,
            callback=callback,
        )

        self._register(cliDef, cmd)

        return cmd


    def _build_root_group(self, cliDef: CliDef) -> click.Group:
        root = click.Group(name=cliDef.key, help=cliDef.help)

        self._register(cliDef, root)

        # 引数
        self._attach_params(root, cliDef.arguments)

        # コマンド
        self._attach_commands(root, cliDef.commands)

        return root


    def _build_command(self, cmdDef: CommandDef) -> click.Command:

        params = [self._build_param(arg) for arg in cmdDef.arguments]
        # collect arguments from template
        for tmpl_cmd in cmdDef.get_templates():
            params.extend([self._build_param(arg) for arg in tmpl_cmd.arguments])

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
            hidden=cmdDef.is_template
        )

        self._register(cmdDef, cmd)

        return cmd


    def _build_param(self, arg: ArgumentDef):

        if arg.option:
            # option
            param = click.Option(
                #[arg.option, arg.key], # works but ...
                [arg.option] + (arg.aliases or []),
                help=arg.help,
                default=arg.default,
                is_flag=arg.is_flag or False,
            )
            param.name = arg.key
        else:
            # positional
            param = click.Argument(
                param_decls=[arg.key],
                #nargs=self.to_nargs(arg.mult),
            )
            self.apply_mult(param, arg.mult)

        self._register(arg, param)

        return param


    def _attach_commands(self, parent, commands: Iterable[CommandDef]):
        for cmd in commands or []:
            parent.add_command(self._build_command(cmd))


    def _attach_params(self, cmd, arguments):
        for arg in arguments or []:
            cmd.params.append(self._build_param(arg))

    # def to_nargs(self, mult: MultDef) -> str | int | None:
    #     if mult is None:
    #         return None

    #     if mult.is_fixed: # lower == upper
    #         return mult.lower

    #     if mult.is_optional:
    #         return "?"

    #     if mult.is_unbounded:
    #         if mult.lower == 0:
    #             return "*"
    #         elif mult.lower == 1:
    #             return "+"
        
    #     return f"{mult.lower}..{mult.upper}"


    def apply_mult(self, param, mult: MultDef):
        if mult.is_fixed:
            param.nargs = mult.lower
        elif mult.is_unbounded:
            param.multiple = True
        elif mult.is_optional:
            param.nargs = 1
