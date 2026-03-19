import pytest
from typing import Any
from pytest import fixture
from pathlib import Path
import click
from click.testing import CliRunner
import re

from cli_def import (
    CliDefParser,
    CliDef,
)
from cli_def.click import ClickBuilder

@fixture
def minimum_cli_def_path() -> str:
    return "tests/data/cli_def_minimum.toml"
    
@fixture
def simple_cli_def_path() -> str:
    return "tests/data/cli_def_simple.toml"

@fixture
def command_cli_def_path() -> str:
    return "tests/data/cli_def_command.toml"

@fixture
def command_w_template_cli_def_path() -> str:
    return "tests/data/cli_def_command_w_template.toml"

@fixture
def subcommand_cli_def_path() -> str:
    return "tests/data/cli_def_subcommand.toml"

# def sample_cli_definition_path() -> str:
#     #return Path.relative_to(Path.cwd(), "resource/test.toml")
#     return "resources/test.toml"

# whether key:val entry is in output
def is_entry_in(key: str, val: Any, output: str) -> Any:
    return re.search(f"{key!r}: {val!r}", output)


def test_arg_parser_minimum(minimum_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(minimum_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build_click(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0,result.output
    assert "Usage" in result.output, result.output

    result = runner.invoke(cli, [])
    assert result.exit_code == 0,result.output
    assert "/MyCLI " in result.output, result.output


def test_cli_def_parser_simple(simple_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(simple_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build_click(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()

    result = runner.invoke(cli, [])

    assert result.exit_code == 2, result.output
    assert "Usage" in result.output
    assert "positional_param1".upper() in result.output, result.output


    result = runner.invoke(cli, ["param1"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI " in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", None, result.output)
    assert is_entry_in("flag_option", False, result.output)
    assert is_entry_in("choice_option", "a", result.output)
    
    result = runner.invoke(cli, ["param1", "--option", "MYOPTION", "--flag", "--choice", "c"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI " in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", "MYOPTION", result.output)
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "c", result.output)


    result = runner.invoke(cli, ["param1", "param2"])
    assert result.exit_code == 2, result.output

#     input1 = ["param1", "param2"]
#     parsed, remain = arg_parser.parse_known_args(input1)
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option is None
#     assert parsed.flag_option == False
#     assert parsed.choice_option == "a"
#     assert len(remain) == 1
#     assert remain == ["param2"]

#     input2 = ["param1", "param2", "--option", "value_for_option"]
#     parsed, remain = arg_parser.parse_known_args(input2)
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option == "value_for_option"
#     assert parsed.flag_option == False
#     assert parsed.choice_option == "a"
#     assert len(remain) == 1
#     assert remain == ["param2"]

#     input3 = ["param1", "param2", "--option", "value_for_option", "--flag"]
#     parsed, remain = arg_parser.parse_known_args(input3)
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option == "value_for_option"
#     assert parsed.flag_option == True
#     assert parsed.choice_option == "a"
#     assert len(remain) == 1
#     assert remain == ["param2"]

#     input4 = ["param1", "param2", "--option", "value_for_option", "--flag", "--choice", "b"]
#     parsed, remain = arg_parser.parse_known_args(input4)
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option == "value_for_option"
#     assert parsed.flag_option == True
#     assert parsed.choice_option == "b"
#     assert len(remain) == 1
#     assert remain == ["param2"]

    
def test_arg_parser_command(command_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(command_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build_click(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    result = runner.invoke(cli, ["command1"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1" in result.output, result.output
#     input1 = ["command1", "param1"]
#     parsed, remain = arg_parser.parse_known_args(input1)
#     assert parsed.command == "command1", parsed
#     assert len(remain) == 1
#     assert "param1" in remain

#     input2 = ["command2", "param1", "--option", "value_of_option", "--flag"]
#     parsed, remain = arg_parser.parse_known_args(input2)
#     assert parsed.command == "command2", parsed
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option == "value_of_option"
#     assert parsed.flag_option == True
#     assert len(remain) == 0

#     input3 = ["command3", "param1", "--option", "value_of_option", "--flag"]
#     parsed, remain = arg_parser.parse_known_args(input3)
#     assert parsed.command == "command3", parsed
#     assert len(remain) == 4
#     assert remain == ["param1", "--option", "value_of_option", "--flag"]


# def test_arg_parser_command_w_template(command_w_template_cli_def_path):
#     cliDef = parse_cli_definition(command_w_template_cli_def_path)
#     assert cliDef is not None
#     builder = ClickBuilder()
#     arg_parser = builder.build_click(cliDef)
#     assert arg_parser is not None

#     for node in cliDef.iter_all_nodes():
#         assert node.defpath in builder.defpath_mapping

#     input1 = ["command1", "param1"]
#     parsed, remain = arg_parser.parse_known_args(input1)
#     assert parsed.command == "command1", parsed
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option is None
#     assert parsed.flag_option == False
#     assert len(remain) == 0

#     input2 = ["command2", "param1", "--option", "value_of_option", "--flag"]
#     parsed, remain = arg_parser.parse_known_args(input2)
#     assert parsed.command == "command2", parsed
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option == "value_of_option"
#     assert parsed.flag_option == True
#     assert len(remain) == 0

#     input3 = ["command3", "param1", "--option", "value_of_option", "--flag"]
#     parsed, remain = arg_parser.parse_known_args(input3)
#     assert parsed.command == "command3", parsed
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option == "value_of_option"
#     assert parsed.flag_option == True
#     assert len(remain) == 0


def test_arg_parser_subcommand(subcommand_cli_def_path):
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(subcommand_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build_click(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    result = runner.invoke(cli, ["command1", "subcommand1_1"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_1" in result.output, result.output
#     input1 = ["command1", "subcommand1_1"]
#     parsed, remain = arg_parser.parse_known_args(input1)
#     assert parsed.command == "command1", parsed
#     assert parsed.subcommand == "subcommand1_1", parsed
#     assert len(remain) == 0

#     input1 = ["command1", "subcommand1_2", "param1"]
#     parsed, remain = arg_parser.parse_known_args(input1)
#     assert parsed.command == "command1", parsed
#     assert parsed.subcommand == "subcommand1_2", parsed
#     assert "param1" in parsed.positional_param1
#     assert parsed.optional_option is None
#     assert parsed.flag_option == False
#     assert len(remain) == 0
