from io import BytesIO

import pytest

from translate.storage.html import htmlfile


def parse_html(src: str) -> htmlfile:
    f = BytesIO(src.encode("utf-8"))
    f.name = "test.html"
    return htmlfile(f)


def test_html_context_basic():
    """Test that basic context is extracted correctly from HTML."""
    store = parse_html('<div data-translate-context="greeting">Hello world</div>')
    units = store.getunits()
    assert any(
        u.getcontext() == "greeting" and u.source == "Hello world" for u in units
    )


def test_html_context_attribute():
    """Test that attribute is added to context."""
    store = parse_html(
        '<p data-translate-context="intro" title="Hello world">Welcome!</p>'
    )
    units = store.getunits()
    unit0 = units[0]
    unit1 = units[1]
    assert unit0.getcontext() == "intro[title]"
    assert unit0.source == "Hello world"
    assert unit1.getcontext() == "intro"
    assert unit1.source == "Welcome!"


def test_html_context_attribute_with_id():
    """Test that attributes get context hints from element IDs when duplicated."""
    src = '<p id="a" title="Hello">World</p><p id="b" title="Hello">Universe</p>'
    store = parse_html(src)
    title_units = [u for u in store.getunits() if u.source == "Hello"]
    assert len(title_units) == 2
    contexts = {u.getcontext() for u in title_units}
    assert contexts == {"test.html:a[title]", "test.html:b[title]"}


def test_html_context_same_source_different_contexts():
    """Test that the same source with different contexts is differentiated."""
    store = parse_html(
        '<p data-translate-context="one">Hello</p><p data-translate-context="two">Hello</p>'
    )
    hello_units = [u for u in store.getunits() if u.source == "Hello"]
    contexts = sorted({u.getcontext() for u in hello_units})
    assert contexts == ["one", "two"]
    # Ensure ids differ
    assert len({u.getid() for u in hello_units}) == 2


def test_html_context_nested_outer_wins():
    """
    Test that outer context applies to outer unit.

    This test uses nested translatable elements (p inside div)
    so that inner becomes its own unit.
    """
    src = (
        '<div data-translate-context="outer">Start '
        '<p data-translate-context="inner">Inner</p> End</div>'
    )
    store = parse_html(src)
    inner = [u for u in store.getunits() if u.source == "Inner"]
    outer = [
        u
        for u in store.getunits()
        if "Start" in u.source or "End" in u.source or u.source.startswith("Start")
    ]
    # Inner unit should have inner context
    assert inner
    assert inner[0].getcontext() == "inner"
    # At least one outer fragment should carry outer context
    assert any(u.getcontext() == "outer" for u in outer)


def test_html_context_absent():
    """Test that absence of context is handled correctly."""
    store = parse_html("<p>No context here</p>")
    try:
        unit = next(u for u in store.getunits() if u.source == "No context here")
    except StopIteration:
        pytest.fail("Unit with 'No context here' source was not found!")
    assert unit.getcontext() == ""


def test_html_context_id_overridden_by_explicit():
    """Test that data-translate-context overrides id fallback."""
    store = parse_html('<p id="greeting" data-translate-context="ctx">Hello</p>')
    units = [u for u in store.getunits() if u.source == "Hello"]
    assert units
    assert units[0].getcontext() == "ctx"


def test_html_context_id_not_used_when_no_duplicates():
    """Test that ID is not used when there are no duplicate sources."""
    src = '<p id="a">Hello</p><p id="b">World</p>'
    store = parse_html(src)
    try:
        hello_unit = next(u for u in store.getunits() if u.source == "Hello")
    except StopIteration:
        pytest.fail("Unit with 'Hello' source was not found!")
    try:
        world_unit = next(u for u in store.getunits() if u.source == "World")
    except StopIteration:
        pytest.fail("Unit with 'World' source was not found!")
    assert hello_unit.getcontext() == ""
    assert world_unit.getcontext() == ""


def test_html_context_id_not_used_when_data_translate_context_identical():
    """Test that identical data-translate-context has the same context."""
    store = parse_html(
        '<p data-translate-context="greet">Hello</p><div id="lala"><span data-translate-context="greet">Hello</span></div>'
    )
    hello_units = [u for u in store.getunits() if u.source == "Hello"]
    assert len(hello_units) == 1
    assert len(hello_units[0].getlocations()) == 2
    assert hello_units[0].getcontext() == "greet"


def test_html_context_disambiguates_duplicates_with_id():
    """Test that ID is used to disambiguate when the same source appears multiple times."""
    src = '<p id="a">Hello</p><p id="b">Hello</p>'
    store = parse_html(src)
    hello_units = [u for u in store.getunits() if u.source == "Hello"]
    assert len(hello_units) == 2
    contexts = {u.getcontext() for u in hello_units}
    # Both should be distinct contexts on the basis of their IDs
    assert contexts == {"test.html:a", "test.html:b"}


def test_html_context_disambiguates_duplicates_with_ancestor_id():
    """Test that when identical sources are under different ancestor IDs, ancestor path hints are applied."""
    src = (
        '<div id="section_a"><p>Hello</p></div>\n<div id="section_b"><p>Hello</p></div>'
    )
    store = parse_html(src)
    units = [u for u in store.getunits() if u.source == "Hello"]
    assert len(units) == 2
    ctx1 = units[0].getcontext()
    ctx2 = units[1].getcontext()
    assert ctx1 == "test.html+section_a.p:0-20"
    assert ctx2 == "test.html+section_b.p:0-20"
