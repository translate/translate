from io import BytesIO

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
        unit = None
    assert unit is not None
    assert unit.getcontext() == ""


def test_html_context_id_fallback_basic():
    """Test that when data-translate-context is absent, the id attribute fallback is used."""
    store = parse_html('<p id="greeting">Hello world</p>')
    units = [u for u in store.getunits() if u.source == "Hello world"]
    assert units
    assert units[0].getcontext() == "greeting"


def test_html_context_id_overridden_by_explicit():
    """Test that data-translate-context overrides id fallback."""
    store = parse_html('<p id="greeting" data-translate-context="ctx">Hello</p>')
    units = [u for u in store.getunits() if u.source == "Hello"]
    assert units
    assert units[0].getcontext() == "ctx"
