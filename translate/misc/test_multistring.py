# -*- coding: utf-8 -*-
import pytest

from translate.misc import multistring


class TestMultistring:

    def test_constructor(self):
        t = multistring.multistring
        s1 = t("test")
        assert type(s1) == t
        assert s1 == "test"
        assert s1.strings == ["test"]
        s2 = t(["test", u"mé"])
        assert type(s2) == t
        assert repr(s2) == 'multistring([test,mé])'
        assert s2 == "test"
        assert s2.strings == ["test", u"mé"]
        assert s2 != s1
        pytest.raises(ValueError, t, [])

    def test_replace(self):
        t = multistring.multistring
        s1 = t(["abcdef", "def"])

        result = s1.replace("e", "")
        assert type(result) == t
        assert result == t(["abcdf", "df"])

        result = s1.replace("e", "xx")
        assert result == t(["abcdxxf", "dxxf"])

        result = s1.replace("e", u"\xe9")
        assert result == t([u"abcd\xe9f", u"d\xe9f"])

        result = s1.replace("e", "\n")
        assert result == t([u"abcd\nf", u"d\nf"])

        result = result.replace("\n", "\\n")
        assert result == t([u"abcd\\nf", u"d\\nf"])

        result = result.replace("\\n", "\n")
        assert result == t([u"abcd\nf", u"d\nf"])

        s2 = t(["abcdeef", "deef"])

        result = s2.replace("e", "g")
        assert result == t([u"abcdggf", u"dggf"])

        result = s2.replace("e", "g", 1)
        assert result == t([u"abcdgef", u"dgef"])

    def test_comparison(self):
        t = multistring.multistring
        assert t("test") == "test"
        assert t("test").__cmp__("test") == 0

        assert t(u"téßt") > "test"
        assert "test" < t(u"téßt")
        assert t(u"téßt").__cmp__("test") > 0

    def test_coercion(self):
        t = multistring.multistring
        assert str(t("test")) == "test"
        assert str(t(u"téßt")) == "téßt"
