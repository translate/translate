#!/usr/bin/env python

"""tests decoration handling functions that are used by checks"""

from translate.filters import decoration

def test_spacestart():
    """test operation of spacestart()"""
    assert decoration.spacestart("  Start") == "  "
    assert decoration.spacestart(u"\u0020\u00a0Start") == u"\u0020\u00a0"
    # non-breaking space
    assert decoration.spacestart(u"\u00a0\u202fStart") == u"\u00a0\u202f"
    # zero width space
    assert decoration.spacestart(u"\u200bStart") == u"\u200b"
    # Some exotic spaces
    assert decoration.spacestart(u"\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200aStart") == u"\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"

def test_find_marked_variables():
    """check that we cna identify variables correctly, first value is start location, i
    second is avtual variable sans decoations"""
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
    variables = decoration.findmarkedvariables("The &variable.variable; string", "&", ";")
    assert variables == [(4, "variable.variable")]

