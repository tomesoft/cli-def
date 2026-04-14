# tests/cli_def/core/models/raw/arg_def_test.py
import pytest

from cli_def.core.models.raw import ArgumentDef
from cli_def.core.models.raw import CommandDef
from cli_def.core.models.resolved import ResolvedCommandDef, ResolvedArgumentDef

def test_cmd_def_basic_1():
    cmd_def = ResolvedCommandDef("my_key", definition=CommandDef("dummy"))

    assert cmd_def.key == "my_key"
    assert cmd_def.help is None
    assert cmd_def.parent is None
    assert cmd_def.entrypoint is None
    assert cmd_def.group is None
    assert cmd_def.arguments == []
    assert cmd_def.subcommands == []
    assert cmd_def.is_leaf
    assert cmd_def.extra_defs == {}
    assert cmd_def.bound_params == {}
    assert cmd_def.definition.key == "dummy"

def test_cmd_def_basic_2():
    cmd_def = ResolvedCommandDef(
        "my_key",
        definition=CommandDef("dummy"),
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bound_params={"param1":"value1"},
    )

    assert cmd_def.key == "my_key"
    assert cmd_def.help == "MY_HELP"
    assert cmd_def.parent is None
    assert cmd_def.entrypoint == "MY_ENTRYPOINT"
    assert cmd_def.group == "MY_GROUP"
    assert cmd_def.arguments == []
    assert cmd_def.subcommands == []
    assert cmd_def.is_leaf
    assert cmd_def.extra_defs == {}
    assert cmd_def.bound_params == {"param1": "value1"}
    assert cmd_def.definition.key == "dummy"


def test_cmd_def_basic_3():
    cmd_def = ResolvedCommandDef(
        "my_key",
        help="MY_HELP",
        definition=CommandDef("dummy"),
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        arguments=[ResolvedArgumentDef("dummyArg", definition=ArgumentDef("dummy2"))],
        subcommands=[ResolvedCommandDef("dummyCmd", definition=CommandDef("dummy3"))],
        bound_params={"param1":"value1"},
        extra_defs={"extra_spec1":"extra_value1"},
    )

    assert cmd_def.key == "my_key"
    assert cmd_def.help == "MY_HELP"
    assert cmd_def.parent is None
    assert cmd_def.entrypoint == "MY_ENTRYPOINT"
    assert cmd_def.group == "MY_GROUP"
    assert cmd_def.arguments != []
    assert cmd_def.subcommands != []
    assert not cmd_def.is_leaf
    assert cmd_def.extra_defs == {"extra_spec1":"extra_value1"}
    assert cmd_def.bound_params == {"param1": "value1"}
    assert cmd_def.definition.key == "dummy"
