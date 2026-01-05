import pytest

from translate.misc import dictutils


def test_cidict_has_key() -> None:
    cid = dictutils.cidict()
    cid["lower"] = "lowercase"
    assert "lower" in cid
    assert "Lower" in cid
    assert "LOWER" in cid
    assert "upper" not in cid


def test_cidict_pop() -> None:
    cid = dictutils.cidict()
    cid["lower"] = "lowercase"
    assert cid.pop("LOWER")
    with pytest.raises(KeyError):
        assert cid.pop("upper")


def test_cidict_getitem() -> None:
    cid = dictutils.cidict()
    cid["lower"] = "lowercase"
    assert cid["lower"] == "lowercase"
    assert cid["LOWER"] == "lowercase"
    assert cid["Lower"] == "lowercase"
    with pytest.raises(KeyError):
        assert cid["upper"]


def test_cidict_setitem() -> None:
    cid = dictutils.cidict()
    cid["lower"] = "lowercase"
    cid["Lower"] = "other"
    assert cid["lower"] == "other"


def test_cidict_delitem() -> None:
    cid = dictutils.cidict()
    cid["lower"] = "lowercase"
    del cid["Lower"]
    assert "lower" not in cid
