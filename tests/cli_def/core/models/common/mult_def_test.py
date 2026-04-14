import pytest

from cli_def.core.models.common import MultDef


def test_mult_def_1():
    mult = MultDef.from_str("1")
    assert mult == MultDef(1, 1)
    assert mult.is_fixed
    assert not mult.is_optional
    assert not mult.is_unbounded

    mult = MultDef.from_str("?")
    assert mult == MultDef(0, 1)
    assert not mult.is_fixed
    assert mult.is_optional
    assert not mult.is_unbounded

    mult = MultDef.from_str("*")
    assert mult == MultDef(0, None)
    assert not mult.is_fixed
    assert not mult.is_optional
    assert mult.is_unbounded

    mult = MultDef.from_str("+")
    assert mult == MultDef(1, None)
    assert not mult.is_fixed
    assert not mult.is_optional
    assert mult.is_unbounded

    mult = MultDef.from_str("2..3")
    assert mult == MultDef(2, 3)
    assert not mult.is_fixed
    assert not mult.is_optional
    assert not mult.is_unbounded

    mult = MultDef.from_str("2..*")
    assert mult == MultDef(2, None)
    assert not mult.is_fixed
    assert not mult.is_optional
    assert mult.is_unbounded

def test_mult_def_2():
    mult = MultDef.from_str("1")
    assert mult.to_str() == "1"

    mult = MultDef.from_str("?")
    assert mult.to_str() == "?"

    mult = MultDef.from_str("*")
    assert mult.to_str() == "*"

    mult = MultDef.from_str("+")
    assert mult.to_str() == "+"

    mult = MultDef.from_str("2..3")
    assert mult.to_str() == "2..3"

    mult = MultDef.from_str("2..*")
    assert mult.to_str() == "2..*"


def test_mult_def_from_any_int_1():
    mult = MultDef.from_any(2)
    assert mult == MultDef(2, 2)

def test_mult_def_from_any_tuple_1():
    mult = MultDef.from_any((1, 2))
    assert mult == MultDef(1, 2)

def test_mult_def_from_any_list_1():
    mult = MultDef.from_any([3, 5])
    assert mult == MultDef(3, 5)

def test_mult_def_from_any_mapping_1():
    mult = MultDef.from_any({"lower": 3, "upper":4})
    assert mult == MultDef(3, 4)