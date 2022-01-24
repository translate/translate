import pytest

from translate.misc import multistring


class TestMultistring:
    @staticmethod
    def test_constructor():
        t = multistring.multistring
        s1 = t("test")
        assert type(s1) is t
        assert s1 == "test"
        assert s1.strings == ["test"]
        s2 = t(["test", "mé"])
        assert type(s2) is t
        assert s2 == "test"
        assert s2.strings == ["test", "mé"]
        assert s2 != s1
        with pytest.raises(ValueError):
            t([])

    @staticmethod
    def test_repr():
        t = multistring.multistring
        s1 = t("test")
        assert repr(s1) == "multistring(['test'])"
        assert eval("multistring.%s" % repr(s1)) == s1

        s2 = t(["test", "mé"])
        assert repr(s2) == "multistring(['test', 'mé'])"
        assert eval("multistring.%s" % repr(s2)) == s2

    @staticmethod
    def test_replace():
        t = multistring.multistring
        s1 = t(["abcdef", "def"])

        result = s1.replace("e", "")
        assert type(result) is t
        assert result == t(["abcdf", "df"])

        result = s1.replace("e", "xx")
        assert result == t(["abcdxxf", "dxxf"])

        result = s1.replace("e", "\xe9")
        assert result == t(["abcd\xe9f", "d\xe9f"])

        result = s1.replace("e", "\n")
        assert result == t(["abcd\nf", "d\nf"])

        result = result.replace("\n", "\\n")
        assert result == t(["abcd\\nf", "d\\nf"])

        result = result.replace("\\n", "\n")
        assert result == t(["abcd\nf", "d\nf"])

        s2 = t(["abcdeef", "deef"])

        result = s2.replace("e", "g")
        assert result == t(["abcdggf", "dggf"])

        result = s2.replace("e", "g", 1)
        assert result == t(["abcdgef", "dgef"])

    @staticmethod
    def test_comparison():
        t = multistring.multistring
        assert t("test") == "test"
        assert t("test").__cmp__("test") == 0

        assert t("téßt") > "test"
        assert "test" < t("téßt")
        assert t("téßt").__cmp__("test") > 0

    @staticmethod
    def test_coercion():
        t = multistring.multistring
        assert str(t("test")) == "test"
        assert str(t("téßt")) == "téßt"

    @staticmethod
    def test_unicode_coercion():
        t = multistring.multistring
        assert str(t("test")) == "test"
        assert str(t("test")) == "test"
        assert str(t("téßt")) == "téßt"
        assert str(t("téßt")) == "téßt"
        assert str(t(["téßt", "blāh"])) == "téßt"
        assert str(t(["téßt"])) == "téßt"

    @staticmethod
    def test_list_coercion():
        t = multistring.multistring
        assert str([t("test")]) == "[multistring(['test'])]"
        assert str([t("tést")]) == "[multistring(['tést'])]"

    @staticmethod
    def test_multistring_hash():
        t = multistring.multistring
        foo = t(["foo", "bar"])
        foodict = {foo: "baz"}
        assert "foo" in foodict
        foodict2 = {"foo": "baz"}
        assert foo in foodict2
        assert hash(str(foo)) == hash(foo)
