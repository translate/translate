from translate.storage import pocommon


def test_roundtrip_quote_plus() -> None:
    """Test that what we put in is what we get out."""

    def roundtrip_quote_plus(text, quoted) -> None:
        quote = pocommon.quote_plus(text)
        assert quote == quoted
        unquote = pocommon.unquote_plus(quoted)
        assert unquote == text

    roundtrip_quote_plus("abc", "abc")
    roundtrip_quote_plus("key space", "key%20space")
    roundtrip_quote_plus("key ḓey", "key%20%E1%B8%93ey")
    roundtrip_quote_plus(
        "path/file.c(2):3,path space/file.h:4", "path/file.c(2):3,path%20space/file.h:4"
    )
    roundtrip_quote_plus("[uid1@example.com]SUMMARY", "[uid1@example.com]SUMMARY")


def test_unescaped_plus_characters() -> None:
    """Test that + characters in locations are preserved correctly."""

    def roundtrip_quote_plus(text, quoted) -> None:
        quote = pocommon.quote_plus(text)
        assert quote == quoted
        unquote = pocommon.unquote_plus(quoted)
        assert unquote == text

    # Plus signs should be encoded as %2B and decoded back to +
    roundtrip_quote_plus("DLG_WORKFLOW+101", "DLG_WORKFLOW%2B101")
    roundtrip_quote_plus("Button+OK", "Button%2BOK")
    roundtrip_quote_plus("Menu+File+Save", "Menu%2BFile%2BSave")
    
    # Test that unencoded + in source is preserved (not converted to space)
    assert pocommon.unquote_plus("DLG_WORKFLOW+101") == "DLG_WORKFLOW+101"
    assert pocommon.unquote_plus("Button+OK") == "Button+OK"
    
    # Mixed case: both + and space
    roundtrip_quote_plus("Item +OK Button", "Item%20%2BOK%20Button")
