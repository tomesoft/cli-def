# tests/cli_def/core/models/raw/arg_def_test.py
import pytest

from cli_def.core.models.raw import CliDef
from cli_def.core.models.raw import ArgumentDef
from cli_def.core.models.raw import CommandDef

def test_cli_def_basic_1():
    cli_def = CliDef("my_key")

    assert cli_def.key == "my_key"
    assert cli_def.help is None
    assert cli_def.parent is None
    assert cli_def.entrypoint is None
    assert cli_def.group is None
    assert cli_def.bind == {}
    assert cli_def.arguments == []
    assert cli_def.prompt is None
    assert cli_def.include == []
    assert cli_def.commands == []
    assert cli_def.is_leaf
    assert cli_def.extra_defs == {}

def test_cli_def_basic_2():
    cli_def = CliDef(
        "my_key",
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bind={"param1":"value1"},
        prompt="MY_PROMPT",
        include=["my_include.toml"],
    )

    assert cli_def.key == "my_key"
    assert cli_def.help == "MY_HELP"
    assert cli_def.parent is None
    assert cli_def.entrypoint == "MY_ENTRYPOINT"
    assert cli_def.group == "MY_GROUP"
    assert cli_def.bind == {"param1": "value1"}
    assert cli_def.arguments == []
    assert cli_def.prompt == "MY_PROMPT"
    assert cli_def.include == ["my_include.toml"]
    assert cli_def.commands == []
    assert cli_def.is_leaf
    assert cli_def.extra_defs == {}

def test_cli_def_basic_3():
    cli_def = CliDef(
        "my_key",
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bind={"param1":"value1"},
        arguments=[ArgumentDef("dummyArg")],
        prompt="MY_PROMPT",
        include=["my_include.toml"],
        commands=[CommandDef("dummyCmd")],
        extra_defs={"extra_spec1":"extra_value1"}
    )

    assert cli_def.key == "my_key"
    assert cli_def.help == "MY_HELP"
    assert cli_def.parent is None
    assert cli_def.entrypoint == "MY_ENTRYPOINT"
    assert cli_def.group == "MY_GROUP"
    assert cli_def.bind == {"param1": "value1"}
    assert cli_def.arguments != []
    assert cli_def.prompt == "MY_PROMPT"
    assert cli_def.commands != []
    assert cli_def.include == ["my_include.toml"]
    assert not cli_def.is_leaf
    assert cli_def.extra_defs == {"extra_spec1":"extra_value1"}

def test_cli_def_override_1():
    cli_def_base = CliDef(
        "my_key",
        help="MY_HELP",
        entrypoint="MY_ENTRYPOINT",
        group="MY_GROUP",
        bind={"param1":"value1"},
        arguments=[ArgumentDef("dummyArg")],
        prompt="MY_PROMPT",
        include=["my_include.toml"],
        commands=[CommandDef("dummyCmd")],
        extra_defs={"extra_spec1":"extra_value1"}
    )
    cli_def = CliDef("my_key2")
    cli_def.override_with(cli_def_base)

    assert cli_def.key == "my_key2"
    assert cli_def.help == "MY_HELP"
    assert cli_def.parent is None
    assert cli_def.entrypoint == "MY_ENTRYPOINT"
    assert cli_def.group == "MY_GROUP"
    assert cli_def.bind == {"param1": "value1"}
    assert cli_def.arguments == []
    assert cli_def.prompt == "MY_PROMPT"
    assert cli_def.commands == []
    assert cli_def.include == []
    assert cli_def.is_leaf
    assert cli_def.extra_defs == {"extra_spec1":"extra_value1"}
