# tests/cli_def/argparse_guilder_test.py
import pytest
from pytest import fixture
from pathlib import Path
import argparse

from cli_def import (
    CliDefParser,
    CliDef,
)
from cli_def.backend.argparse import ArgparseBuilder

def data_path() -> Path:
    return Path(__file__).parent.parent.parent / "data"

@fixture
def minimum_cli_def_path() -> str:
    return str(data_path() / "cli_def_minimum.toml")

@fixture
def hello_world_cli_def_path() -> str:
    return str(data_path() / "cli_def_hello_world.toml")
    
@fixture
def simple_cli_def_path() -> str:
    return str(data_path() / "cli_def_simple.toml")

@fixture
def command_cli_def_path() -> str:
    return str(data_path() / "cli_def_command.toml")

@fixture
def command_w_template_cli_def_path() -> str:
    return str(data_path() / "cli_def_command_w_template.toml")

@fixture
def subcommand_cli_def_path() -> str:
    return str(data_path() / "cli_def_subcommand.toml")

@fixture
def subcommand_w_template_cli_def_path() -> str:
    return str(data_path() / "cli_def_subcommand_w_template.toml")

# def sample_cli_definition_path() -> str:
#     #return Path.relative_to(Path.cwd(), "resource/test.toml")
#     return "resources/test.toml"

def test_argparse_builder_hello_world(hello_world_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(hello_world_cli_def_path)
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)

    parsed = arg_parser.parse_args(["John"])
    assert "John" in parsed.your_name


def test_argparse_builder_minimum(minimum_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(minimum_cli_def_path)
    assert cliDef is not None
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)
    assert arg_parser is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    parsed, remain = arg_parser.parse_known_args(["unexpected_param"])
    assert not hasattr(parsed, "unexpected_param")
    assert len(remain) == 1


def test_cli_def_parser_simple(simple_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(simple_cli_def_path)
    assert cliDef is not None
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)
    assert arg_parser is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    input1 = ["param1", "unexpected_param"]
    parsed, remain = arg_parser.parse_known_args(input1)
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option is None
    assert parsed.flag_option == False
    assert parsed.choice_option == "a"
    assert len(remain) == 1
    assert remain == ["unexpected_param"]

    input2 = ["param1", "unexpected_param", "--option", "value_for_option"]
    parsed, remain = arg_parser.parse_known_args(input2)
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option == "value_for_option"
    assert parsed.flag_option == False
    assert parsed.choice_option == "a"
    assert len(remain) == 1
    assert remain == ["unexpected_param"]

    input3 = ["param1", "unexpected_param", "--option", "value_for_option", "--flag"]
    parsed, remain = arg_parser.parse_known_args(input3)
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option == "value_for_option"
    assert parsed.flag_option == True
    assert parsed.choice_option == "a"
    assert len(remain) == 1
    assert remain == ["unexpected_param"]

    input4 = ["param1", "unexpected_param", "--option", "value_for_option", "--flag", "--choice", "b"]
    parsed, remain = arg_parser.parse_known_args(input4)
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option == "value_for_option"
    assert parsed.flag_option == True
    assert parsed.choice_option == "b"
    assert len(remain) == 1
    assert remain == ["unexpected_param"]

    
def test_argparse_builder_command(command_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(command_cli_def_path)
    assert cliDef is not None
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)
    assert arg_parser is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    input1 = ["command1", "param1"]
    parsed, remain = arg_parser.parse_known_args(input1)
    assert parsed.command == "command1", parsed
    assert len(remain) == 1
    assert "param1" in remain

    input2 = ["command2", "param1", "--option", "value_of_option", "--flag"]
    parsed, remain = arg_parser.parse_known_args(input2)
    assert parsed.command == "command2", parsed
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option == "value_of_option"
    assert parsed.flag_option == True
    assert len(remain) == 0

    input3 = ["command3", "param1", "--option", "value_of_option", "--flag"]
    parsed, remain = arg_parser.parse_known_args(input3)
    assert parsed.command == "command3", parsed
    assert len(remain) == 4
    assert remain == ["param1", "--option", "value_of_option", "--flag"]


def test_argparse_builder_command_w_template(command_w_template_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(command_w_template_cli_def_path)
    assert cliDef is not None
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)
    assert arg_parser is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    input1 = ["command1", "param1"]
    parsed, remain = arg_parser.parse_known_args(input1)
    assert parsed.command == "command1", parsed
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option is None
    assert parsed.flag_option == False
    assert parsed.choice_option == "a"
    assert len(remain) == 0

    input2 = ["command2", "param1", "--option", "value_of_option", "--flag", "--choice", "b"]
    parsed, remain = arg_parser.parse_known_args(input2)
    assert parsed.command == "command2", parsed
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option == "value_of_option"
    assert parsed.flag_option == True
    assert parsed.choice_option == "b"
    assert len(remain) == 0

    input3 = ["command3", "param1", "--option", "value_of_option", "--flag", "--choice", "c"]
    parsed, remain = arg_parser.parse_known_args(input3)
    assert parsed.command == "command3", parsed
    assert parsed.flag_option == True
    assert parsed.choice_option == "c"
    assert len(remain) == 3
    assert remain == ["param1", "--option", "value_of_option"]

    input4 = ["command4", "param1", "--option", "value_of_option", "--flag", "--choice", "c"]
    parsed, remain = arg_parser.parse_known_args(input4)
    assert parsed.command == "command4", parsed
    assert len(remain) == 6
    assert remain == input4[1:]


def test_argparse_builder_subcommand(subcommand_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(subcommand_cli_def_path)
    assert cliDef is not None
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)
    assert arg_parser is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    input1 = ["command1", "subcommand1_1"]
    parsed, remain = arg_parser.parse_known_args(input1)
    assert parsed.command == "command1", parsed
    assert parsed.subcommand == "subcommand1_1", parsed
    assert len(remain) == 0

    input1 = ["command1", "subcommand1_2", "param1"]
    parsed, remain = arg_parser.parse_known_args(input1)
    assert parsed.command == "command1", parsed
    assert parsed.subcommand == "subcommand1_2", parsed
    assert "param1" in parsed.positional_param1
    assert parsed.optional_option is None
    assert parsed.flag_option == False
    assert len(remain) == 0


def test_argparse_builder_subcommand_w_template(subcommand_w_template_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(subcommand_w_template_cli_def_path)
    assert cliDef is not None
    builder = ArgparseBuilder()
    arg_parser = builder.build_argparse(cliDef)
    assert arg_parser is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    input1 = ["command1", "subcommand1_1", "param1"]
    parsed, remain = arg_parser.parse_known_args(input1)
    assert parsed.command == "command1", parsed
    assert parsed.subcommand == "subcommand1_1", parsed
    assert "param1" in parsed.positional_param1, parsed
    assert parsed.optional_option is None
    assert parsed.flag_option == False
    assert parsed.choice_option == "a"
    assert len(remain) == 0

    input2 = ["command1", "subcommand1_2", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    parsed, remain = arg_parser.parse_known_args(input2)
    assert parsed.command == "command1", parsed
    assert parsed.subcommand == "subcommand1_2", parsed
    assert "param1" in parsed.positional_param1, parsed
    assert parsed.optional_option == "myoption"
    assert parsed.flag_option == True
    assert parsed.choice_option == "b"
    assert len(remain) == 0

    input3 = ["command1", "subcommand1_3", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    parsed, remain = arg_parser.parse_known_args(input3)
    assert parsed.command == "command1", parsed
    assert parsed.subcommand == "subcommand1_3", parsed
    assert parsed.flag_option == True
    assert parsed.choice_option == "b"
    assert remain == ["param1", "--option", "myoption"]

    input4 = ["command1", "subcommand1_4", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    parsed, remain = arg_parser.parse_known_args(input4)
    assert parsed.command == "command1", parsed
    assert parsed.subcommand == "subcommand1_4", parsed
    assert remain == input4[2:]


    input5 = ["command2", "subcommand2_1", "param1"]
    parsed, remain = arg_parser.parse_known_args(input5)
    assert parsed.command == "command2", parsed
    assert parsed.subcommand == "subcommand2_1", parsed
    assert "param1" in parsed.positional_param2, parsed
    assert parsed.optional_option2 is None
    assert parsed.flag_option2 == False
    assert parsed.choice_option2 == "a"
    assert len(remain) == 0

    input2 = ["command2", "subcommand2_2", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    parsed, remain = arg_parser.parse_known_args(input2)
    assert parsed.command == "command2", parsed
    assert parsed.subcommand == "subcommand2_2", parsed
    assert "param1" in parsed.positional_param2, parsed
    assert parsed.optional_option2 == "myoption"
    assert parsed.flag_option2 == True
    assert parsed.choice_option2 == "b"
    assert len(remain) == 0
