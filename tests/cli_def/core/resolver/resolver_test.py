import pytest
from pytest import fixture
from pathlib import Path

from cli_def.core.models import (
    CliDef,
    ResolvedCliDef,
    ResolvedArgumentDef,
    MultDef,
)
from cli_def.core.parser import (
    CliDefParser,
)
from cli_def.core.resolver import CliDefResolver

def data_path() -> Path:
    return Path(__file__).parent.parent.parent.parent / "data"

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

@fixture
def include_base_cli_def_path():
    return data_path() / "cli_def_include_base.toml"

@fixture
def include_base_cmd_cli_def_path():
    return data_path() / "cli_def_include_base_cmd.toml"



def prepare_raw_cli_def(path: Path) -> CliDef:
    parser = CliDefParser()
    raw_cli_def = parser.parse_from_toml(path)
    assert raw_cli_def
    return raw_cli_def



def test_cli_def_resolver_minimum(minimum_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(minimum_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.key == "MinimumCLI"
    assert result.defpath == "/MinimumCLI"
    assert result.deflevel == 0
    assert result.help == "HELP", result
    assert len(result.arguments) == 0
    assert result.commands is not None
    assert len(result.commands) == 0

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 1


def test_cli_def_resolver_simple(simple_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(simple_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
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


def test_cli_def_resolver_command(command_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(command_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.key == "MyCLI"
    assert result.defpath == "/MyCLI"
    assert result.help == "HELP", result

    assert result.commands is not None
    assert len(result.commands) == 4
    cmd1, cmd2, cmd3, cmd4 = result.commands
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.deflevel == 1
    assert cmd1.help == "HELP of command1"
    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"

    assert len(cmd1.arguments) == 0

    assert len(cmd2.arguments) == 4

    def check_a1(arg: ResolvedArgumentDef, defpath_expected: str):
        assert arg.key == "positional_param1"
        assert arg.defpath == defpath_expected
        assert arg.deflevel == 2
        assert arg.option == None
        assert arg.mult == MultDef(1, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 1
        assert arg.extra_defs["spec_type"] == "path"

    a1 = cmd2.arguments[0]
    assert not a1.has_bound_value
    check_a1(a1, "/MyCLI/command2/positional_param1")


    def check_a2(arg: ResolvedArgumentDef):
        assert arg.key == "optional_option"
        #assert arg.defpath == "/MyCLI/command2/optional_option"
        assert arg.option == "--option"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 0

    a2 = cmd2.arguments[1]
    assert not a2.has_bound_value
    check_a2(a2)

    def check_a3(arg: ResolvedArgumentDef):
        assert arg.key == "flag_option"
        #assert arg.defpath == "/MyCLI/command2/flag_option"
        assert arg.is_flag
        assert arg.option == "--flag"
        assert arg.default == False
        assert len(arg.extra_defs) == 0

    a3 = cmd2.arguments[2]
    assert not a3.has_bound_value
    check_a3(a3)

    def check_a4(arg: ResolvedArgumentDef):
        assert arg.key == "choice_option"
        #assert arg.defpath == "/MyCLI/command2/choice_option"
        assert arg.option == "--choice"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert arg.choices == ["a", "b", "c"]
        assert arg.default == "a"
        assert len(arg.extra_defs) == 0

    a4 = cmd2.arguments[3]
    assert not a4.has_bound_value
    check_a4(a4)

    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert len(cmd3.arguments) == 0

    assert cmd4.key == "command4"
    assert cmd4.defpath == "/MyCLI/command4"
    assert cmd4.help == "HELP of command4"
    assert cmd4.bound_params == {"positional_param1": "fixed"}
    assert len(cmd4.arguments) == 4
    check_a1(cmd4.arguments[0], "/MyCLI/command4/positional_param1")
    check_a2(cmd4.arguments[1])
    check_a3(cmd4.arguments[2])
    check_a4(cmd4.arguments[3])
    assert cmd4.arguments[0].has_bound_value
    assert cmd4.arguments[0].bound_value == "fixed"
    assert not cmd4.arguments[1].has_bound_value
    assert not cmd4.arguments[2].has_bound_value
    assert not cmd4.arguments[3].has_bound_value

    assert cmd4.bound_params == {"positional_param1": "fixed"}

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 13


def test_cli_def_resolver_command_w_template(command_w_template_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(command_w_template_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.key == "MyCLI"
    assert result.help == "HELP", result

    assert len(result.commands) == 4
    cmd1, cmd2, cmd3, cmd4 = result.commands

    # assert cmd_tmpl_1.key == "_command_templ_1"
    # assert cmd_tmpl_1.defpath == "/MyCLI/_command_templ_1"
    # assert cmd_tmpl_1.is_template
    # assert cmd_tmpl_1.help is None
    # assert cmd_tmpl_2.key == "_command_templ_2"
    # assert cmd_tmpl_2.defpath == "/MyCLI/_command_templ_2"
    # assert cmd_tmpl_2.is_template
    # assert cmd_tmpl_2.help is None
    def check_a1(arg: ResolvedArgumentDef):
        assert arg.key == "positional_param1"
        #assert arg.defpath == "/MyCLI/_command_templ_1/positional_param1"
        assert arg.option == None
        assert arg.mult == MultDef(1, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 1
        assert arg.extra_defs["spec_type"] == "path"

    def check_a2(arg: ResolvedArgumentDef):
        assert arg.key == "optional_option"
        #assert arg.defpath == "/MyCLI/_command_templ_1/optional_option"
        assert arg.option == "--option"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 0

    def check_a3(arg: ResolvedArgumentDef):
        assert arg.key == "flag_option"
        #assert arg.defpath == "/MyCLI/_command_templ_2/flag_option"
        assert arg.option == "--flag"
        assert arg.is_flag
        assert arg.default == False

    def check_a4(arg: ResolvedArgumentDef):
        assert arg.key == "choice_option"
        #assert arg.defpath == "/MyCLI/_command_templ_2/choice_option"
        assert arg.option == "--choice"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert arg.choices == ["a", "b", "c"]
        assert arg.default == "a"
        assert len(arg.extra_defs) == 0

    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.help == "HELP of command1"
    assert len(cmd1.arguments) == 4
    a1, a2, a3, a4 = cmd1.arguments
    check_a1(a1)
    check_a2(a2)
    check_a3(a3)
    check_a4(a4)

    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"
    assert len(cmd2.arguments) == 4
    a1, a2, a3, a4 = cmd2.arguments
    check_a1(a1)
    check_a2(a2)
    check_a3(a3)
    check_a4(a4)

    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert len(cmd3.arguments) == 2
    a3, a4 = cmd3.arguments
    check_a3(a3)
    check_a4(a4)

    assert cmd4.key == "command4"
    assert cmd4.defpath == "/MyCLI/command4"
    assert cmd4.help == "HELP of command4"
    assert len(cmd4.arguments) == 0

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 15


def test_cli_def_resolver_subcommand(subcommand_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(subcommand_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None

    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.help == "HELP", result

    assert len(result.commands) == 3
    cmd1, cmd2, cmd3 = result.commands
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.help == "HELP of command1"
    assert len(cmd1.subcommands) == 3
    subcmd1_1, subcmd1_2, subcmd1_3 = cmd1.subcommands

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


    assert subcmd1_3.key == "subcommand1_3"
    assert subcmd1_3.defpath == "/MyCLI/command1/subcommand1_3"
    assert subcmd1_3.deflevel == 2
    assert subcmd1_3.help == "HELP of subcommand1_3"
    assert subcmd1_3.bound_params == {"positional_param1": "fixed"}

    assert len(subcmd1_3.arguments) == 4
    argdef0 = subcmd1_3.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/MyCLI/command1/subcommand1_3/positional_param1"
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert argdef0.bound_value == "fixed"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = subcmd1_3.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/MyCLI/command1/subcommand1_3/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0
    argdef2 = subcmd1_3.arguments[2]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/MyCLI/command1/subcommand1_3/flag_option"
    assert argdef2.option == "--flag"
    assert argdef2.is_flag
    assert argdef2.default == False
    argdef3 = subcmd1_3.arguments[3]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/MyCLI/command1/subcommand1_3/choice_option"
    assert argdef3.option == "--choice"
    assert argdef3.mult == MultDef(0, 1)
    assert argdef3.type == "str"
    assert argdef3.choices == ["a", "b", "c"]
    assert argdef3.default == "a"
    assert len(argdef3.extra_defs) == 0



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


    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert cmd3.subcommands == []

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 17


def test_cli_def_resolver_subcommand_w_template(subcommand_w_template_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(subcommand_w_template_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.help == "HELP", result

    assert len(result.commands) == 4
    cmd1, cmd2, cmd3, cmd4 = result.commands
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/MyCLI/command1"
    assert cmd1.help == "HELP of command1"
    assert len(cmd1.subcommands) == 4
    subcmd1_1, subcmd1_2, subcmd1_3, subcmd1_4 = cmd1.subcommands

    def check_a1(arg: ResolvedArgumentDef):
        assert arg.key == "positional_param1"
        #assert arg.defpath == "/MyCLI/command1/_subcommand_templ_1/positional_param1"
        assert arg.option == None
        assert arg.mult == MultDef(1, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 1
        assert arg.extra_defs["spec_type"] == "path"

    def check_a2(arg: ResolvedArgumentDef):
        assert arg.key == "optional_option"
        #assert arg.defpath == "/MyCLI/command1/_subcommand_templ_1/optional_option"
        assert arg.option == "--option"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 0

    def check_a3(arg: ResolvedArgumentDef):
        assert arg.key == "flag_option"
        #assert arg.defpath == "/MyCLI/command1/_subcommand_templ_2/flag_option"
        assert arg.option == "--flag"
        assert arg.is_flag
        assert arg.default == False

    def check_a4(arg: ResolvedArgumentDef):
        assert arg.key == "choice_option"
        #assert arg.defpath == "/MyCLI/command1/_subcommand_templ_2/choice_option"
        assert arg.option == "--choice"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert arg.choices == ["a", "b", "c"]
        assert arg.default == "a"
        assert len(arg.extra_defs) == 0


    assert subcmd1_1.key == "subcommand1_1"
    assert subcmd1_1.defpath == "/MyCLI/command1/subcommand1_1"
    assert subcmd1_1.deflevel == 2
    assert subcmd1_1.help == "HELP of subcommand1_1"
    assert len(subcmd1_1.arguments) == 4
    check_a1(subcmd1_1.arguments[0])
    check_a2(subcmd1_1.arguments[1])
    check_a3(subcmd1_1.arguments[2])
    check_a4(subcmd1_1.arguments[3])


    assert subcmd1_2.key == "subcommand1_2"
    assert subcmd1_2.defpath == "/MyCLI/command1/subcommand1_2"
    assert subcmd1_2.deflevel == 2
    assert subcmd1_2.help == "HELP of subcommand1_2"
    assert len(subcmd1_2.arguments) == 4
    check_a1(subcmd1_2.arguments[0])
    check_a2(subcmd1_2.arguments[1])
    check_a3(subcmd1_2.arguments[2])
    check_a4(subcmd1_2.arguments[3])

    assert subcmd1_3.key == "subcommand1_3"
    assert subcmd1_3.defpath == "/MyCLI/command1/subcommand1_3"
    assert subcmd1_3.deflevel == 2
    assert subcmd1_3.help == "HELP of subcommand1_3"
    assert len(subcmd1_3.arguments) == 2
    check_a3(subcmd1_3.arguments[0])
    check_a4(subcmd1_3.arguments[1])

    assert subcmd1_4.key == "subcommand1_4"
    assert subcmd1_4.defpath == "/MyCLI/command1/subcommand1_4"
    assert subcmd1_4.deflevel == 2
    assert subcmd1_4.help == "HELP of subcommand1_4"
    assert len(subcmd1_4.arguments) == 0


    assert cmd2.key == "command2"
    assert cmd2.defpath == "/MyCLI/command2"
    assert cmd2.help == "HELP of command2"
    assert len(cmd2.subcommands) == 2
    subcmd2_1, subcmd2_2 = cmd2.subcommands

    def check_a2_1(arg: ResolvedArgumentDef):
        assert arg.key == "positional_param2"
        #assert arg.defpath == "/MyCLI/command2/_subcommand2/positional_param2"
        assert arg.option == None
        assert arg.mult == MultDef(1, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 1
        assert arg.extra_defs["spec_type"] == "path"

    def check_a2_2(arg: ResolvedArgumentDef):
        assert arg.key == "optional_option2"
        #assert arg.defpath == "/MyCLI/command2/_subcommand2/optional_option2"
        assert arg.option == "--option"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert len(arg.extra_defs) == 0

    def check_a2_3(arg: ResolvedArgumentDef):
        assert arg.key == "flag_option2"
        #assert arg.defpath == "/MyCLI/command2/_subcommand2/flag_option2"
        assert arg.option == "--flag"
        assert arg.is_flag
        assert arg.default == False

    def check_a2_4(arg: ResolvedArgumentDef):
        assert arg.key == "choice_option2"
        #assert arg.defpath == "/MyCLI/command2/_subcommand2/choice_option2"
        assert arg.option == "--choice"
        assert arg.mult == MultDef(0, 1)
        assert arg.type == "str"
        assert arg.choices == ["a", "b", "c"]
        assert arg.default == "a"
        assert len(arg.extra_defs) == 0

    assert subcmd2_1.key == "subcommand2_1"
    assert subcmd2_1.defpath == "/MyCLI/command2/subcommand2_1"
    assert subcmd2_1.deflevel == 2
    assert subcmd2_1.help == "HELP of subcommand2_1"
    assert subcmd2_1.bound_params == {"positional_param2": "fixed2_1"}
    assert len(subcmd2_1.arguments) == 4
    check_a2_1(subcmd2_1.arguments[0])
    check_a2_2(subcmd2_1.arguments[1])
    check_a2_3(subcmd2_1.arguments[2])
    check_a2_4(subcmd2_1.arguments[3])
    assert subcmd2_1.arguments[0].has_bound_value
    assert subcmd2_1.arguments[0].bound_value == "fixed2_1"
    assert not subcmd2_1.arguments[1].has_bound_value
    assert not subcmd2_1.arguments[2].has_bound_value
    assert not subcmd2_1.arguments[3].has_bound_value

    assert subcmd2_2.key == "subcommand2_2"
    assert subcmd2_2.defpath == "/MyCLI/command2/subcommand2_2"
    assert subcmd2_2.deflevel == 2
    assert subcmd2_2.help == "HELP of subcommand2_2"
    assert len(subcmd2_2.arguments) == 4
    assert subcmd2_2.bound_params == {"positional_param2": "fixed2_2"}
    check_a2_1(subcmd2_2.arguments[0])
    check_a2_2(subcmd2_2.arguments[1])
    check_a2_3(subcmd2_2.arguments[2])
    check_a2_4(subcmd2_2.arguments[3])
    assert subcmd2_2.arguments[0].has_bound_value
    assert subcmd2_2.arguments[0].bound_value == "fixed2_2"
    assert not subcmd2_2.arguments[1].has_bound_value
    assert not subcmd2_2.arguments[2].has_bound_value
    assert not subcmd2_2.arguments[3].has_bound_value


    assert cmd3.key == "command3"
    assert cmd3.defpath == "/MyCLI/command3"
    assert cmd3.help == "HELP of command3"
    assert cmd3.subcommands == []
    assert cmd3.arguments == []

    assert cmd4.key == "command4"
    assert cmd4.defpath == "/MyCLI/command4"
    assert cmd4.help == "HELP of command4"
    assert cmd4.bound_params == {"positional_param1": "fixed4", "optional_option": "fixed_option4"}
    assert cmd4.subcommands == []
    assert len(cmd4.arguments) == 2
    check_a1(cmd4.arguments[0])
    check_a2(cmd4.arguments[1])
    assert cmd4.arguments[0].has_bound_value
    assert cmd4.arguments[0].bound_value == "fixed4"
    assert cmd4.arguments[1].has_bound_value
    assert cmd4.arguments[1].bound_value == "fixed_option4"
    

    nodes = list(result.iter_all_nodes())
    assert len(nodes) == 31



def test_cli_def_resolver_include(include_base_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(include_base_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.help == "HELP", result

    assert result.key == "BaseCLI"
    assert result.defpath == "/BaseCLI"
    assert result.help == "HELP", result
    assert len(result.arguments) == 4
    argdef0 = result.arguments[0]
    assert argdef0.key == "positional_param1"
    assert argdef0.defpath == "/BaseCLI/positional_param1"
    assert argdef0.deflevel == 1
    assert argdef0.option == None
    assert argdef0.mult == MultDef(1, 1)
    assert argdef0.type == "str"
    assert len(argdef0.extra_defs) == 1
    assert argdef0.extra_defs["spec_type"] == "path"
    argdef1 = result.arguments[1]
    assert argdef1.key == "optional_option"
    assert argdef1.defpath == "/BaseCLI/optional_option"
    assert argdef1.option == "--option"
    assert argdef1.mult == MultDef(0, 1)
    assert argdef1.type == "str"
    assert len(argdef1.extra_defs) == 0
    argdef2 = result.arguments[2]
    assert argdef2.key == "flag_option"
    assert argdef2.defpath == "/BaseCLI/flag_option"
    assert argdef2.option == "--flag"
    assert argdef2.mult == MultDef(0, 1)
    assert argdef2.type == "bool"
    assert argdef2.is_flag
    # assert len(argdef2.extra_defs) == 1
    # assert argdef2.extra_defs["action"] == "store_true"
    argdef3 = result.arguments[3]
    assert argdef3.key == "choice_option"
    assert argdef3.defpath == "/BaseCLI/choice_option"
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


def test_cli_def_resolver_include_cmd(include_base_cmd_cli_def_path):
    raw_cli_def = prepare_raw_cli_def(include_base_cmd_cli_def_path)
    result = CliDefResolver().resolve(raw_cli_def)
    assert result is not None
    assert result is not None
    assert isinstance(result, ResolvedCliDef)
    assert result.help == "HELP", result

    assert result.commands is not None
    assert len(result.commands) == 2
    cmd1, cmd2 = result.commands
    assert cmd1.key == "command1"
    assert cmd1.defpath == "/BaseCLI/command1"
    assert cmd1.deflevel == 1
    assert cmd1.help == "HELP of command1"
    assert cmd2.key == "command2"
    assert cmd2.defpath == "/BaseCLI/command2"
    assert cmd2.help == "HELP of command2"
    assert len(cmd2.arguments) == 4