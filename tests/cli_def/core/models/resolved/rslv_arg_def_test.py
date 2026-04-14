# tests/cli_def/core/models/raw/arg_def_test.py
import pytest

from cli_def.core.models.raw import ArgumentDef
from cli_def.core.models.resolved import ResolvedArgumentDef
from cli_def.core.models.common import MultDef

def test_arg_def_basic_1():
    arg_def = ResolvedArgumentDef("my_key", definition=ArgumentDef("dummy"))

    assert arg_def.key == "my_key"
    assert arg_def.help is None
    assert arg_def.parent is None
    assert arg_def.option is None
    assert arg_def.aliases == []
    assert arg_def.choices is None
    assert arg_def.default is None
    assert arg_def.dest is None
    assert arg_def.is_flag is None
    assert arg_def.type is None
    assert arg_def.mult == MultDef(1, 1)
    assert arg_def.is_leaf
    assert arg_def.is_positional
    assert arg_def.extra_defs == {}
    assert arg_def.definition.key == "dummy"

def test_arg_def_basic_2():
    arg_def = ResolvedArgumentDef("my_key", definition=ArgumentDef("dummy"), option="--option")

    assert arg_def.key == "my_key"
    assert arg_def.help is None
    assert arg_def.parent is None
    assert arg_def.option == "--option"
    assert arg_def.aliases == []
    assert arg_def.choices is None
    assert arg_def.default is None
    assert arg_def.dest is None
    assert arg_def.is_flag is None
    assert arg_def.type is None
    assert arg_def.mult == MultDef(0, 1)
    assert arg_def.is_leaf
    assert not arg_def.is_positional
    assert arg_def.extra_defs == {}
    assert arg_def.definition.key == "dummy"

def test_arg_def_basic_3():
    input = {
        "key": "my_key",
        "help": "My HELP",
        "dest": "destination",
        "aliases": ["-O"],
        "option": "--option",
        "choices": ["A", "B", "C"],
        "default": "B",
        "type": "str",
        "is_flag": False,
        "mult": 1,
    }
    arg_def = ResolvedArgumentDef(definition=ArgumentDef("dummy"), **input)

    assert arg_def.key == "my_key"
    assert arg_def.help == "My HELP"
    assert arg_def.parent is None
    assert arg_def.option == "--option"
    assert arg_def.aliases == ["-O"]
    assert arg_def.choices == ["A", "B", "C"]
    assert arg_def.default == "B"
    assert arg_def.dest == "destination"
    assert arg_def.is_flag is False
    assert arg_def.type == "str"
    assert arg_def.mult == MultDef(1, 1)
    assert arg_def.is_leaf
    assert not arg_def.is_positional
    assert arg_def.extra_defs == {}
    assert arg_def.definition.key == "dummy"

# def test_arg_def_from_mapping_1():
#     input = {
#         "key": "my_key",
#         "help": "My HELP",
#         "dest": "destination",
#         "aliases": ["-O"],
#         "option": "--option",
#         "choices": ["A", "B", "C"],
#         "default": "B",
#         "type": "str",
#         "is_flag": False,
#         "mult": 1,
#         "extra_spec_type": "path"
#     }
#     arg_def = ResolvedArgumentDef.from_mapping(input)

#     assert arg_def.key == "my_key"
#     assert arg_def.help == "My HELP"
#     assert arg_def.parent is None
#     assert arg_def.option == "--option"
#     assert arg_def.aliases == ["-O"]
#     assert arg_def.choices == ["A", "B", "C"]
#     assert arg_def.default == "B"
#     assert arg_def.dest == "destination"
#     assert arg_def.is_flag is False
#     assert arg_def.type == "str"
#     assert arg_def.mult == MultDef(1, 1)
#     assert arg_def.is_leaf
#     assert not arg_def.is_positional
#     assert arg_def.extra_defs == {"extra_spec_type": "path"}
