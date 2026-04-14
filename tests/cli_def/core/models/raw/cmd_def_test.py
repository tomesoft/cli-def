# tests/cli_def/core/models/raw/arg_def_test.py
import pytest

from cli_def.core.models.raw import ArgumentDef
from cli_def.core.models.raw import CommandDef

def test_cmd_def_basic_1():
    cmd_def = CommandDef("my_key")

    assert cmd_def.key == "my_key"
    assert cmd_def.help is None
    assert cmd_def.parent is None
    assert cmd_def.entrypoint is None
    assert cmd_def.group is None
    assert cmd_def.bind == {}
    assert cmd_def.arguments == []
    assert cmd_def.subcommands == []
    assert cmd_def.is_leaf
    assert cmd_def.extra_defs == {}

def test_cmd_def_basic_2():
    cmd_def = CommandDef(
        "my_key",
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bind={"param1":"value1"},
    )

    assert cmd_def.key == "my_key"
    assert cmd_def.help == "MY_HELP"
    assert cmd_def.parent is None
    assert cmd_def.entrypoint == "MY_ENTRYPOINT"
    assert cmd_def.group == "MY_GROUP"
    assert cmd_def.bind == {"param1": "value1"}
    assert cmd_def.arguments == []
    assert cmd_def.subcommands == []
    assert cmd_def.is_leaf
    assert cmd_def.extra_defs == {}

def test_cmd_def_basic_3():
    cmd_def = CommandDef(
        "my_key",
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bind={"param1":"value1"},
        arguments=[ArgumentDef("dummyArg")],
        subcommands=[CommandDef("dummyCmd")],
        extra_defs={"extra_spec1":"extra_value1"},
    )

    assert cmd_def.key == "my_key"
    assert cmd_def.help == "MY_HELP"
    assert cmd_def.parent is None
    assert cmd_def.entrypoint == "MY_ENTRYPOINT"
    assert cmd_def.group == "MY_GROUP"
    assert cmd_def.bind == {"param1": "value1"}
    assert cmd_def.arguments != []
    assert cmd_def.subcommands != []
    assert not cmd_def.is_leaf
    assert cmd_def.extra_defs == {"extra_spec1":"extra_value1"}

def test_cmd_def_override_1():
    cmd_def_base = CommandDef(
        "my_key",
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bind={"param1":"value1"},
        arguments=[ArgumentDef("dummyArg")],
        subcommands=[CommandDef("dummyCmd")],
        extra_defs={"extra_spec1":"extra_value1"},
    )
    cmd_def = CommandDef("my_key2")
    cmd_def.override_with(cmd_def_base)

    assert cmd_def.key == "my_key2"
    assert cmd_def.help == "MY_HELP"
    assert cmd_def.parent is None
    assert cmd_def.entrypoint == "MY_ENTRYPOINT"
    assert cmd_def.group == "MY_GROUP"
    assert cmd_def.bind == {"param1": "value1"}
    assert cmd_def.arguments == []
    assert cmd_def.subcommands == []
    assert cmd_def.is_leaf
    assert cmd_def.extra_defs == {"extra_spec1":"extra_value1"}
