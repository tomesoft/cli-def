# tests/cli_def/core/models/generic/node_test.py
import pytest

from cli_def.core.models.generic import (
    AbstractCliDefNode,
    AbstractArgumentDef,
    AbstractExecutableNode,
    AbstractCommandDef,
    AbstractCliDef,
)

def test_generic_node_basic_1():
    x = AbstractCliDefNode("key")

def test_generic_node_basic_2():
    x = AbstractArgumentDef("key")

def test_generic_node_basic_3():
    x = AbstractExecutableNode("key")

def test_generic_node_basic_4():
    x = AbstractCommandDef("key")

def test_generic_node_basic_5():
    x = AbstractCliDef("key")