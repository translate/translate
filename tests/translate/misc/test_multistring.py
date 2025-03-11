import pytest

from translate.misc.multistring import multistring


class TestMultistring:
    def test_constructor(self):
        s1 = multistring("test")
        assert type(s1) is multistring
        assert s1 == "test"
        assert s1.strings == ["test"]
        s2 = multistring(["test", "mé"])
        assert type(s2) is multistring
        assert s2 == "test"
        assert s2.strings == ["test", "mé"]
        assert s2 != s1

    def test_constructor_validation(self):
        with pytest.raises(ValueError):
            multistring([])
        with pytest.raises(TypeError):
            multistring([1])
        with pytest.raises(TypeError):
            multistring(["one", None])

    def test_repr(self):
        s1 = multistring("test")
        assert repr(s1) == "multistring(['test'])"
        assert eval(f"{s1!r}") == s1  # noqa: S307

        s2 = multistring(["test", "mé"])
        assert repr(s2) == "multistring(['test', 'mé'])"
        assert eval(f"{s2!r}") == s2  # noqa: S307

    def test_replace(self):
        s1 = multistring(["abcdef", "def"])

        result = s1.replace("e", "")
        assert type(result) is multistring
        assert result == multistring(["abcdf", "df"])

        result = s1.replace("e", "xx")
        assert result == multistring(["abcdxxf", "dxxf"])

        result = s1.replace("e", "\xe9")
        assert result == multistring(["abcd\xe9f", "d\xe9f"])

        result = s1.replace("e", "\n")
        assert result == multistring(["abcd\nf", "d\nf"])

        result = result.replace("\n", "\\n")
        assert result == multistring(["abcd\\nf", "d\\nf"])

        result = result.replace("\\n", "\n")
        assert result == multistring(["abcd\nf", "d\nf"])

        s2 = multistring(["abcdeef", "deef"])

        result = s2.replace("e", "g")
        assert result == multistring(["abcdggf", "dggf"])

        result = s2.replace("e", "g", 1)
        assert result == multistring(["abcdgef", "dgef"])

    def test_comparison(self):
        assert multistring("test") == "test"
        assert multistring("test") == multistring("test")

        assert multistring("téßt") > "test"
        assert multistring("téßt") > multistring("test")

        assert multistring("téßt") > "test"
        assert multistring("test") < multistring("téßt")

    def test_coercion(self):
        assert str(multistring("test")) == "test"
        assert str(multistring("téßt")) == "téßt"

    def test_unicode_coercion(self):
        assert str(multistring("test")) == "test"
        assert str(multistring("test")) == "test"
        assert str(multistring("téßt")) == "téßt"
        assert str(multistring("téßt")) == "téßt"
        assert str(multistring(["téßt", "blāh"])) == "téßt"
        assert str(multistring(["téßt"])) == "téßt"

    def test_list_coercion(self):
        assert str([multistring("test")]) == "[multistring(['test'])]"
        assert str([multistring("tést")]) == "[multistring(['tést'])]"

    def test_multistring_hash(self):
        foo = multistring(["foo", "bar"])
        foodict = {foo: "baz"}
        assert "foo" in foodict
        foodict2 = {"foo": "baz"}
        assert foo in foodict2
        assert hash(str(foo)) == hash(foo)
