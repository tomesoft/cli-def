import pytest

pytestmark = pytest.mark.click
pytest.importorskip("click")

from typing import Any
from pytest import fixture
from pathlib import Path
import re

import click
from click.testing import CliRunner


from cli_def import (
    CliDefParser,
)

from cli_def.core.models import ResolvedCliDef
from cli_def.core.resolver import CliDefResolver
from cli_def.backend.click import ClickBuilder

def data_path() -> Path:
    return Path(__file__).parent.parent.parent / "data"

@fixture
def minimum_cli_def_path():
    return data_path() / "cli_def_minimum.toml"

@fixture
def hello_world_cli_def_path():
    return data_path() / "cli_def_hello_world.toml"
    
@fixture
def simple_cli_def_path():
    return data_path() / "cli_def_simple.toml"

@fixture
def command_cli_def_path():
    return data_path() / "cli_def_command.toml"

@fixture
def command_w_template_cli_def_path():
    return data_path() / "cli_def_command_w_template.toml"

@fixture
def subcommand_cli_def_path():
    return data_path() / "cli_def_subcommand.toml"

@fixture
def subcommand_w_template_cli_def_path():
    return data_path() / "cli_def_subcommand_w_template.toml"


def prepare_cli_def(path: Path) -> ResolvedCliDef:
    parser = CliDefParser()
    cliDef = parser.parse_from_toml(path)
    assert cliDef is not None
    resolvedCliDef = CliDefResolver().resolve(cliDef)
    return resolvedCliDef

# helper method whether key:val entry is in output
def is_entry_in(key: str, val: Any, output: str) -> Any:
    return re.search(f"{key!r}: {val!r}", output)

def test_click_builder_hello_world(hello_world_cli_def_path):
    cliDef = prepare_cli_def(hello_world_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
    assert cli is not None

    runner = CliRunner()
    result = runner.invoke(cli, ["John"])
    assert result.exit_code == 0,result.output

    assert is_entry_in("your_name", "John", result.output), result.output


def test_click_builder_minimum(minimum_cli_def_path):
    cliDef = prepare_cli_def(minimum_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0,result.output
    assert "Usage" in result.output, result.output

    result = runner.invoke(cli, [])
    assert result.exit_code == 0,result.output
    assert "/MinimumCLI " in result.output, result.output

    result = runner.invoke(cli, ["unexpected_param"])
    # TODO adapt to passthrough
    #assert result.exit_code == 2,result.output
    assert result.exit_code == 0,result.output


def test_click_builder_simple(simple_cli_def_path):
    cliDef = prepare_cli_def(simple_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
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
    assert "/SimpleCLI " in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", None, result.output)
    assert is_entry_in("flag_option", False, result.output)
    assert is_entry_in("choice_option", "a", result.output)
    
    result = runner.invoke(cli, ["param1", "--option", "MYOPTION", "--flag", "--choice", "c"])

    assert result.exit_code == 0, result.output
    assert "/SimpleCLI " in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", "MYOPTION", result.output)
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "c", result.output)

    result = runner.invoke(cli, ["param1", "unexpected_param"])
    # TODO adapt to passthrough
    #assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output


    
def test_click_builder_command(command_cli_def_path):
    cliDef = prepare_cli_def(command_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    result = runner.invoke(cli, ["command1"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1" in result.output, result.output

    result = runner.invoke(cli, ["command1", "unexpected_param"])
    # TODO adapt to passthrough
    #assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output

    result = runner.invoke(cli, ["command2", "param1"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI/command2 " in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", None, result.output)
    assert is_entry_in("flag_option", False, result.output)
    assert is_entry_in("choice_option", "a", result.output)

    input2 = ["command2", "param1", "--option", "value_of_option", "--flag", "--choice", "c"]
    result = runner.invoke(cli, input2)

    assert result.exit_code == 0, result.output
    assert "/MyCLI/command2 " in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", "value_of_option", result.output)
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "c", result.output)

    result = runner.invoke(cli, ["command3", "unexpected_param"])
    # TODO adapt to passthrough
    #assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output


def test_click_builder_command_w_template(command_w_template_cli_def_path):
    cliDef = prepare_cli_def(command_w_template_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()

    input1 = ["command1", "param1"]
    result = runner.invoke(cli, input1)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1" in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", None, result.output)
    assert is_entry_in("flag_option", False, result.output)
    assert is_entry_in("choice_option", "a", result.output)


    input2 = ["command2", "param1", "--option", "value_of_option", "--flag", "--choice", "b"]
    result = runner.invoke(cli, input2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command2" in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", "value_of_option", result.output)
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "b", result.output)


    input3 = ["command3", "param1", "--option", "value_of_option", "--flag", "--choice", "c"]
    result = runner.invoke(cli, input3)
    # TODO adapt to passthrough
    # assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output
    input3_2 = ["command3", "--flag", "--choice", "c"]
    result = runner.invoke(cli, input3_2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command3" in result.output, result.output
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "c", result.output)

    input4 = ["command4", "--flag", "--choice", "c"]
    result = runner.invoke(cli, input4)
    # TODO adapt to passthrough
    #assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output
    input4_2 = ["command4"]
    result = runner.invoke(cli, input4_2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command4" in result.output, result.output


def test_arg_parser_subcommand(subcommand_cli_def_path):
    cliDef = prepare_cli_def(subcommand_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    result = runner.invoke(cli, ["command1", "subcommand1_1"])

    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_1" in result.output, result.output

    input2 = ["command1", "subcommand1_2", "param1"]
    result = runner.invoke(cli, input2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_2" in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", None, result.output)
    assert is_entry_in("flag_option", False, result.output)
    assert is_entry_in("choice_option", "a", result.output)


def test_arg_parser_subcommand_w_template(subcommand_w_template_cli_def_path):
    cliDef = prepare_cli_def(subcommand_w_template_cli_def_path)
    assert cliDef is not None
    builder = ClickBuilder()
    cli = builder.build(cliDef)
    assert cli is not None

    for node in cliDef.iter_all_nodes():
        assert node.defpath in builder.defpath_mapping

    runner = CliRunner()
    input1 = ["command1", "subcommand1_1", "param1"]
    result = runner.invoke(cli, input1)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_1" in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", None, result.output)
    assert is_entry_in("flag_option", False, result.output)
    assert is_entry_in("choice_option", "a", result.output)

    input2 = ["command1", "subcommand1_2", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    result = runner.invoke(cli, input2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_2" in result.output, result.output
    assert is_entry_in("positional_param1", "param1", result.output)
    assert is_entry_in("optional_option", "myoption", result.output)
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "b", result.output)

    input3 = ["command1", "subcommand1_3", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    result = runner.invoke(cli, input3)
    # TODO adapt to passthrough
    # assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output

    input3_2 = ["command1", "subcommand1_3", "--flag", "--choice", "b"]
    result = runner.invoke(cli, input3_2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_3" in result.output, result.output
    assert is_entry_in("flag_option", True, result.output)
    assert is_entry_in("choice_option", "b", result.output)

    input4 = ["command1", "subcommand1_4", "param1", "--option", "myoption", "--flag", "--choice", "b"]
    result = runner.invoke(cli, input4)
    # TODO adapt to passthrough
    #assert result.exit_code == 2, result.output
    assert result.exit_code == 0, result.output

    input4_2 = ["command1", "subcommand1_4"]
    result = runner.invoke(cli, input4_2)
    assert result.exit_code == 0, result.output
    assert "/MyCLI/command1/subcommand1_4" in result.output, result.output