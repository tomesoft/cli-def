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
from cli_def.core.validator import CliDefValidator, CliDefValidationCode

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

@fixture
def validation_cli_def_path():
    return data_path() / "cli_def_validation.toml"


def prepare_resolved_cli_def(path: Path) -> ResolvedCliDef:
    parser = CliDefParser()
    raw_cli_def = parser.parse_from_toml(path)
    assert raw_cli_def
    resolved = CliDefResolver().resolve(raw_cli_def)
    return resolved


def test_cli_def_validator_minimum(minimum_cli_def_path):
    resolved = prepare_resolved_cli_def(minimum_cli_def_path)

    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert not validator.has_errors


def test_cli_def_validator_simple(simple_cli_def_path):
    resolved = prepare_resolved_cli_def(simple_cli_def_path)
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert not validator.has_errors


def test_cli_def_validator_command(command_cli_def_path):
    resolved = prepare_resolved_cli_def(command_cli_def_path)
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert not validator.has_errors


def test_cli_def_validator_command_w_template(command_w_template_cli_def_path):
    resolved = prepare_resolved_cli_def(command_w_template_cli_def_path)
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert not validator.has_errors


def test_cli_def_validator_subcommand(subcommand_cli_def_path):
    resolved = prepare_resolved_cli_def(subcommand_cli_def_path)
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert not validator.has_errors


def test_cli_def_validator_subcommand_w_template(subcommand_w_template_cli_def_path):
    resolved = prepare_resolved_cli_def(subcommand_w_template_cli_def_path)
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert not validator.has_errors


def test_cli_def_validator_validate(validation_cli_def_path):
    resolved = prepare_resolved_cli_def(validation_cli_def_path)
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    assert validator.has_errors, [str(r) for r in validator.records]
    assert len(validator.records) == 7, [str(r) for r in validator.records]

    assert CliDefValidationCode.E_ARG_BOUND_TYPE_ERROR in validator.errors
    assert CliDefValidationCode.E_ARG_NOT_IN_CHOICES in validator.errors
    assert CliDefValidationCode.E_ARG_MULT_ERROR in validator.errors
    assert CliDefValidationCode.W_CMD_UNUSED_BIND in validator.errors
    assert CliDefValidationCode.E_CMD_DUPLICATE_OPTION in validator.errors
    assert CliDefValidationCode.E_CMD_CONFLICT_ALIAS in validator.errors

