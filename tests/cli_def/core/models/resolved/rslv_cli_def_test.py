# tests/cli_def/core/models/raw/arg_def_test.py
import pytest

from cli_def.core.models.raw import CliDef
from cli_def.core.models.raw import ArgumentDef
from cli_def.core.models.raw import CommandDef
from cli_def.core.models.common import MultDef
from cli_def.core.models.resolved import ResolvedCliDef, ResolvedArgumentDef, ResolvedCommandDef

def test_cli_def_basic_1():
    cli_def = ResolvedCliDef("my_key", definition=CliDef("dummy"))

    assert cli_def.key == "my_key"
    assert cli_def.help is None
    assert cli_def.parent is None
    assert cli_def.entrypoint is None
    assert cli_def.group is None
    assert cli_def.arguments == []
    assert cli_def.prompt is None
    assert cli_def.commands == []
    assert cli_def.is_leaf
    assert cli_def.extra_defs == {}
    assert cli_def.bound_params == {}
    assert cli_def.definition.key == "dummy"

def test_cli_def_basic_2():
    cli_def = ResolvedCliDef(
        "my_key",
        definition=CliDef("dummy"),
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        prompt="MY_PROMPT",
        bound_params={"param1":"value1"},
    )

    assert cli_def.key == "my_key"
    assert cli_def.help == "MY_HELP"
    assert cli_def.parent is None
    assert cli_def.entrypoint == "MY_ENTRYPOINT"
    assert cli_def.group == "MY_GROUP"
    assert cli_def.arguments == []
    assert cli_def.prompt == "MY_PROMPT"
    assert cli_def.commands == []
    assert cli_def.is_leaf
    assert cli_def.bound_params == {"param1": "value1"}
    assert cli_def.extra_defs == {}

def test_cli_def_basic_3():
    cli_def = ResolvedCliDef(
        "my_key",
        definition=CliDef("dummy"),
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        arguments=[ResolvedArgumentDef("dummyArg", definition=ArgumentDef("dummy2"))],
        prompt="MY_PROMPT",
        commands=[ResolvedCommandDef("dummyCmd", definition=CommandDef("dummy3"))],
        bound_params={"param1":"value1"},
        extra_defs={"extra_spec1":"extra_value1"}
    )

    assert cli_def.key == "my_key"
    assert cli_def.help == "MY_HELP"
    assert cli_def.parent is None
    assert cli_def.entrypoint == "MY_ENTRYPOINT"
    assert cli_def.group == "MY_GROUP"
    assert cli_def.arguments != []
    assert cli_def.prompt == "MY_PROMPT"
    assert cli_def.commands != []
    assert not cli_def.is_leaf
    assert cli_def.bound_params == {"param1": "value1"}
    assert cli_def.extra_defs == {"extra_spec1":"extra_value1"}
