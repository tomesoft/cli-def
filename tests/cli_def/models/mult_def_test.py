import pytest

from cli_def.models import MultDef


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