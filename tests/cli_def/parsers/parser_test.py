import pytest
from pytest import fixture
from pathlib import Path

from cli_def import (
    CliDefParser,
    CliDef,
)
from cli_def.models import (
    MultDef,
)

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


def test_cli_def_parser_minimum(minimum_cli_def_path):
    parser = CliDefParser()
    result = parser.parse_from_toml(minimum_cli_def_path)
    assert result is not None
    assert isinstance(result, CliDef)
    assert result.key == "MinimumCLI"
    assert result.defpath == "/MinimumCLI"
    assert result.deflevel == 0
    assert result.help == "HELP", result
    assert len(result.arguments) == 0
    assert result.commands is not None
    assert len(result.commands) == 0

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 1


def test_cli_def_parser_simple(simple_cli_def_path):
    parser = CliDefParser()
    result = parser.parse_from_toml(simple_cli_def_path)
    assert result is not None
    assert isinstance(result, CliDef)
    assert result.key == "SimpleCLI"
    assert result.defpath == "/SimpleCLI"
    assert result.help == "HELP", result
    assert len(result.arguments) == 4
    argdef0 = result.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/SimpleCLI/positional_param1"
    assert argdef0.deflevel == 1
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = result.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/SimpleCLI/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0
    argdef2 = result.arguments[2]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/SimpleCLI/flag_option"
    assert argdef2.option == "--flag"
    assert argdef2.mult == MultDef(0, 1)
    assert argdef2.type == "bool"
    assert argdef2.is_flag
    # assert len(argdef2.extra_defs) == 1
    # assert argdef2.extra_defs["action"] == "store_true"
    argdef3 = result.arguments[3]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/SimpleCLI/choice_option"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0

    assert result.commands is not None
    assert len(result.commands) == 0

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 5


def test_cli_def_parser_command(command_cli_def_path):
    parser = CliDefParser()
    result = parser.parse_from_toml(command_cli_def_path)
    assert result is not None
    assert isinstance(result, CliDef)
    assert result.key == "MyCLI"
    assert result.defpath == "/MyCLI"
    assert result.help == "HELP", result

    assert result.commands is not None
    assert len(result.commands) == 4
    cmd1, cmd2, cmd3, cmd4 = result.commands
    assert not cmd1.is_template
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.deflevel == 1
    assert cmd1.help == "HELP of command1"
    assert not cmd2.is_template
    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"

    assert len(cmd1.arguments) == 0

    assert len(cmd2.arguments) == 4
    argdef0 = cmd2.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/MyCLI/command2/positional_param1"
    assert argdef0.deflevel == 2
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = cmd2.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/MyCLI/command2/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0
    argdef2 = cmd2.arguments[2]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/MyCLI/command2/flag_option"
    assert argdef2.is_flag
    assert argdef2.option == "--flag"
    assert argdef2.default == False
    assert len(argdef2.extra_defs) == 0
    argdef3 = cmd2.arguments[3]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/MyCLI/command2/choice_option"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0

    assert not cmd3.is_template
    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert len(cmd3.arguments) == 0

    assert not cmd4.is_template
    assert cmd4.key == "command4"
    assert cmd4.defpath == "/MyCLI/command4"
    assert cmd4.help == "HELP of command4"
    assert len(cmd4.arguments) == 0
    assert cmd4.inherit_from is not None
    assert len(cmd4.inherit_from) == 1
    assert cmd4.inherit_from[0] == "command2"
    assert cmd4.bind == {"positional_param1": "fixed"}

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 9


def test_cli_def_parser_command_w_template(command_w_template_cli_def_path):
    parser = CliDefParser()
    result = parser.parse_from_toml(command_w_template_cli_def_path)
    assert result is not None
    assert isinstance(result, CliDef)
    assert result.key == "MyCLI"
    assert result.help == "HELP", result

    assert len(result.commands) == 6
    cmd_tmpl_1, cmd_tmpl_2, cmd1, cmd2, cmd3, cmd4 = result.commands

    assert cmd_tmpl_1.key == "_command_templ_1"
    assert cmd_tmpl_1.defpath == "/MyCLI/_command_templ_1"
    assert cmd_tmpl_1.is_template
    assert cmd_tmpl_1.help is None
    assert cmd_tmpl_2.key == "_command_templ_2"
    assert cmd_tmpl_2.defpath == "/MyCLI/_command_templ_2"
    assert cmd_tmpl_2.is_template
    assert cmd_tmpl_2.help is None

    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.help == "HELP of command1"
    assert not cmd1.is_template
    assert cmd1.inherit_from is None
    assert len(cmd1.arguments) == 0
    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"
    assert not cmd2.is_template
    assert cmd2.inherit_from == ["_command_templ_1", "_command_templ_2"]
    assert len(cmd2.arguments) == 0
    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert not cmd3.is_template
    assert cmd3.inherit_from == ["_command_templ_2"]
    assert len(cmd3.arguments) == 0
    assert cmd4.key == "command4"
    assert cmd4.defpath == "/MyCLI/command4"
    assert cmd4.help == "HELP of command4"
    assert not cmd4.is_template
    assert cmd4.inherit_from == []
    assert len(cmd4.arguments) == 0

    assert len(cmd_tmpl_1.arguments) == 2
    argdef0 = cmd_tmpl_1.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/MyCLI/_command_templ_1/positional_param1"
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = cmd_tmpl_1.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/MyCLI/_command_templ_1/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0


    assert len(cmd_tmpl_2.arguments) == 2
    argdef2 = cmd_tmpl_2.arguments[0]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/MyCLI/_command_templ_2/flag_option"
    assert argdef2.option == "--flag"
    assert argdef2.is_flag
    assert argdef2.default == False
    argdef3 = cmd_tmpl_2.arguments[1]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/MyCLI/_command_templ_2/choice_option"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0


    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 11


def test_cli_def_parser_subcommand(subcommand_cli_def_path):
    parser = CliDefParser()
    result = parser.parse_from_toml(subcommand_cli_def_path)
    assert result is not None
    assert isinstance(result, CliDef)
    assert result.help == "HELP", result

    assert len(result.commands) == 3
    cmd1, cmd2, cmd3 = result.commands
    assert not cmd1.is_template
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.help == "HELP of command1"
    assert len(cmd1.subcommands) == 2
    subcmd1_1, subcmd1_2 = cmd1.subcommands
    assert subcmd1_1.key == "subcommand1_1"
    assert subcmd1_1.defpath == "/MyCLI/command1/subcommand1_1"
    assert subcmd1_1.deflevel == 2
    assert subcmd1_1.help == "HELP of subcommand1_1"
    assert len(subcmd1_1.arguments) == 0
    assert subcmd1_2.key == "subcommand1_2"
    assert subcmd1_2.defpath == "/MyCLI/command1/subcommand1_2"
    assert subcmd1_2.deflevel == 2
    assert subcmd1_2.help == "HELP of subcommand1_2"
    assert len(subcmd1_2.arguments) == 4
    argdef0 = subcmd1_2.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/MyCLI/command1/subcommand1_2/positional_param1"
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = subcmd1_2.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/MyCLI/command1/subcommand1_2/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0
    argdef2 = subcmd1_2.arguments[2]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/MyCLI/command1/subcommand1_2/flag_option"
    assert argdef2.option == "--flag"
    assert argdef2.is_flag
    assert argdef2.default == False
    argdef3 = subcmd1_2.arguments[3]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/MyCLI/command1/subcommand1_2/choice_option"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0


    assert not cmd2.is_template
    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"
    assert len(cmd2.subcommands) == 2
    subcmd2_1, subcmd2_2 = cmd2.subcommands
    assert subcmd2_1.key == "subcommand2_1"
    assert subcmd2_1.defpath == "/MyCLI/command2/subcommand2_1"
    assert subcmd2_1.deflevel == 2
    assert subcmd2_1.help == "HELP of subcommand2_1"
    assert len(subcmd2_1.arguments) == 0
    assert subcmd2_2.key == "subcommand2_2"
    assert subcmd2_2.defpath == "/MyCLI/command2/subcommand2_2"
    assert subcmd2_2.deflevel == 2
    assert subcmd2_2.help == "HELP of subcommand2_2"
    assert len(subcmd2_2.arguments) == 0


    assert not cmd3.is_template
    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert cmd3.subcommands is None
    assert len(cmd3.arguments) == 0

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 12


def test_cli_def_parser_subcommand_w_template(subcommand_w_template_cli_def_path):
    parser = CliDefParser()
    result = parser.parse_from_toml(subcommand_w_template_cli_def_path)
    assert result is not None
    assert isinstance(result, CliDef)
    assert result.help == "HELP", result

    assert len(result.commands) == 3
    cmd1, cmd2, cmd3 = result.commands
    assert not cmd1.is_template
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.help == "HELP of command1"
    assert len(cmd1.subcommands) == 6
    subcmd1_tmpl_1, subcmd1_tmpl_2, subcmd1_1, subcmd1_2, subcmd1_3, subcmd1_4 = cmd1.subcommands

    assert subcmd1_tmpl_1.key == "_subcommand_templ_1"
    assert subcmd1_tmpl_1.defpath == "/MyCLI/command1/_subcommand_templ_1"
    assert subcmd1_tmpl_1.is_template
    assert subcmd1_tmpl_1.deflevel == 2
    assert len(subcmd1_tmpl_1.arguments) == 2
    argdef0 = subcmd1_tmpl_1.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/MyCLI/command1/_subcommand_templ_1/positional_param1"
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = subcmd1_tmpl_1.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/MyCLI/command1/_subcommand_templ_1/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0

    assert subcmd1_tmpl_2.key == "_subcommand_templ_2"
    assert subcmd1_tmpl_2.defpath == "/MyCLI/command1/_subcommand_templ_2"
    assert subcmd1_tmpl_2.is_template
    assert subcmd1_tmpl_2.deflevel == 2
    assert len(subcmd1_tmpl_2.arguments) == 2
    argdef2 = subcmd1_tmpl_2.arguments[0]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/MyCLI/command1/_subcommand_templ_2/flag_option"
    assert argdef2.option == "--flag"
    assert argdef2.is_flag
    assert argdef2.default == False
    argdef3 = subcmd1_tmpl_2.arguments[1]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/MyCLI/command1/_subcommand_templ_2/choice_option"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0

    assert subcmd1_1.key == "subcommand1_1"
    assert subcmd1_1.defpath == "/MyCLI/command1/subcommand1_1"
    assert subcmd1_1.deflevel == 2
    assert subcmd1_1.help == "HELP of subcommand1_1"
    assert subcmd1_1.inherit_from is None
    assert len(subcmd1_1.arguments) == 0
    assert subcmd1_2.key == "subcommand1_2"
    assert subcmd1_2.defpath == "/MyCLI/command1/subcommand1_2"
    assert subcmd1_2.deflevel == 2
    assert subcmd1_2.help == "HELP of subcommand1_2"
    assert subcmd1_2.inherit_from == ["_subcommand_templ_1", "_subcommand_templ_2"]
    assert len(subcmd1_2.arguments) == 0
    assert subcmd1_3.key == "subcommand1_3"
    assert subcmd1_3.defpath == "/MyCLI/command1/subcommand1_3"
    assert subcmd1_3.deflevel == 2
    assert subcmd1_3.help == "HELP of subcommand1_3"
    assert subcmd1_3.inherit_from == ["_subcommand_templ_2"]
    assert len(subcmd1_3.arguments) == 0
    assert subcmd1_4.key == "subcommand1_4"
    assert subcmd1_4.defpath == "/MyCLI/command1/subcommand1_4"
    assert subcmd1_4.deflevel == 2
    assert subcmd1_4.help == "HELP of subcommand1_4"
    assert subcmd1_4.inherit_from == []
    assert len(subcmd1_4.arguments) == 0


    assert not cmd2.is_template
    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"
    assert len(cmd2.subcommands) == 3
    subcmd2_0, subcmd2_1, subcmd2_2 = cmd2.subcommands
    assert subcmd2_0.key == "_subcommand2"
    assert subcmd2_0.defpath == "/MyCLI/command2/_subcommand2"
    assert subcmd2_0.is_template
    assert subcmd2_0.deflevel == 2
    assert len(subcmd2_0.arguments) == 4
    argdef0 = subcmd2_0.arguments[0]
    assert argdef0.key == "positional_param2"
    assert argdef0.defpath == "/MyCLI/command2/_subcommand2/positional_param2"
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = subcmd2_0.arguments[1]
    assert argdef1.key == "optional_option2"
    assert argdef1.defpath == "/MyCLI/command2/_subcommand2/optional_option2"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0
    argdef2 = subcmd2_0.arguments[2]
    assert argdef2.key == "flag_option2"
    assert argdef2.defpath == "/MyCLI/command2/_subcommand2/flag_option2"
    assert argdef2.option == "--flag"
    assert argdef2.is_flag
    assert argdef2.default == False
    argdef3 = subcmd2_0.arguments[3]
    assert argdef3.key == "choice_option2"
    assert argdef3.defpath == "/MyCLI/command2/_subcommand2/choice_option2"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0

    assert subcmd2_1.key == "subcommand2_1"
    assert subcmd2_1.defpath == "/MyCLI/command2/subcommand2_1"
    assert subcmd2_1.deflevel == 2
    assert subcmd2_1.help == "HELP of subcommand2_1"
    assert len(subcmd2_1.arguments) == 0
    assert subcmd2_2.key == "subcommand2_2"
    assert subcmd2_2.defpath == "/MyCLI/command2/subcommand2_2"
    assert subcmd2_2.deflevel == 2
    assert subcmd2_2.help == "HELP of subcommand2_2"
    assert len(subcmd2_2.arguments) == 0


    assert not cmd3.is_template
    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert cmd3.subcommands is None
    assert len(cmd3.arguments) == 0

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 21