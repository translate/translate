"""tests decoration handling functions that are used by checks"""

from translate.filters import decoration


def test_spacestart():
    """test operation of spacestart()"""
    assert decoration.spacestart("  Start") == "  "
    assert decoration.spacestart("\u0020\u00a0Start") == "\u0020\u00a0"
    # non-breaking space
    assert decoration.spacestart("\u00a0\u202fStart") == "\u00a0\u202f"
    # Some exotic spaces
    assert (
        decoration.spacestart(
            "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200aStart"
        )
        == "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    )


def test_isvalidaccelerator():
    """test the isvalidaccelerator() function"""
    # Mostly this tests the old code path where acceptlist is None
    assert not decoration.isvalidaccelerator("")
    assert decoration.isvalidaccelerator("a")
    assert decoration.isvalidaccelerator("1")
    assert not decoration.isvalidaccelerator("ḽ")
    # Test new code path where we actually have an acceptlist
    assert decoration.isvalidaccelerator("a", "aeiou")
    assert decoration.isvalidaccelerator("ḽ", "ḓṱḽṋṅ")
    assert not decoration.isvalidaccelerator("a", "ḓṱḽṋṅ")


def test_find_marked_variables():
    """
    check that we can identify variables correctly, the first returned
    value is the start location, the second returned value is the actual
    variable sans decoations
    """
    variables = decoration.findmarkedvariables("The <variable> string", "<", ">")
    assert variables == [(4, "variable")]
    variables = decoration.findmarkedvariables("The $variable string", "$", 1)
    assert variables == [(4, "v")]
    variables = decoration.findmarkedvariables("The $variable string", "$", None)
    assert variables == [(4, "variable")]
    variables = decoration.findmarkedvariables("The $variable string", "$", 0)
    assert variables == [(4, "")]
    variables = decoration.findmarkedvariables("The &variable; string", "&", ";")
    assert variables == [(4, "variable")]
    variables = decoration.findmarkedvariables(
        "The &variable.variable; string", "&", ";"
    )
    assert variables == [(4, "variable.variable")]


def test_getnumbers():
    """test operation of getnumbers()"""
    assert decoration.getnumbers("") == []
    assert decoration.getnumbers("No numbers") == []
    assert decoration.getnumbers("Nine 9 nine") == ["9"]
    assert decoration.getnumbers("Two numbers: 2 and 3") == ["2", "3"]
    assert decoration.getnumbers("R5.99") == ["5.99"]
    # TODO fix these so that we are able to consider locale specific numbers
    # assert decoration.getnumbers("R5,99") == ["5.99"]
    # assert decoration.getnumbers("1\u00a0000,99") == ["1000.99"]
    assert decoration.getnumbers("36°") == ["36°"]
    assert decoration.getnumbers("English 123, Bengali \u09e7\u09e8\u09e9") == [
        "123",
        "\u09e7\u09e8\u09e9",
    ]


def test_getfunctions():
    """test operation of getfunctions()"""
    assert decoration.getfunctions("") == []
    assert decoration.getfunctions("There is no function") == []
    assert decoration.getfunctions("Use the getfunction() function.") == [
        "getfunction()"
    ]
    assert decoration.getfunctions(
        "Use the getfunction1() function or the getfunction2() function."
    ) == ["getfunction1()", "getfunction2()"]
    assert decoration.getfunctions("The module.getfunction() method") == [
        "module.getfunction()"
    ]
    assert decoration.getfunctions("The module->getfunction() method") == [
        "module->getfunction()"
    ]
    assert decoration.getfunctions("The module::getfunction() method") == [
        "module::getfunction()"
    ]
    assert decoration.getfunctions("The function().function() function") == [
        "function().function()"
    ]
    assert decoration.getfunctions("Deprecated, use function().") == ["function()"]
    assert decoration.getfunctions("Deprecated, use function() or other().") == [
        "function()",
        "other()",
    ]
