from translate.misc import quote


def test_find_all():
    """Tests the find_all function."""
    assert list(quote.find_all("", "a")) == []
    assert list(quote.find_all("a", "b")) == []
    assert list(quote.find_all("a", "a")) == [0]
    assert list(quote.find_all("aa", "a")) == [0, 1]
    assert list(quote.find_all("abba", "ba")) == [2]  # codespell:ignore
    # check we skip the whole instance
    assert list(quote.find_all("banana", "ana")) == [1]


def test_extract():
    """Tests the extract function."""
    assert quote.extract("the <quoted> part", "<", ">", "\\", 0) == ("<quoted>", False)
    assert quote.extract("the 'quoted' part", "'", "'", "\\", 0) == ("'quoted'", False)
    assert quote.extract("the 'isn\\'t escaping fun' part", "'", "'", "\\", 0) == (
        "'isn\\'t escaping fun'",
        False,
    )
    assert quote.extract("the 'isn\\'t something ", "'", "'", "\\", 0) == (
        "'isn\\'t something ",
        True,
    )
    assert quote.extract("<quoted>\\", "<", ">", "\\", 0) == ("<quoted>", False)
    assert quote.extract("<quoted><again>", "<", ">", "\\", 0) == (
        "<quoted><again>",
        False,
    )
    assert quote.extract("<quoted>\\\\<again>", "<", ">", "\\", 0) == (
        "<quoted><again>",
        False,
    )
    assert quote.extract("<quoted\\>", "<", ">", "\\", 0) == ("<quoted\\>", True)
    assert quote.extract(' -->\n<!ENTITY blah "Some">', "<!--", "-->", None, 1) == (
        " -->",
        False,
    )
    assert quote.extract('">\n', '"', '"', None, True) == ('"', False)


def test_extractwithoutquotes():
    """Tests the extractwithoutquotes function."""
    assert quote.extractwithoutquotes("the <quoted> part", "<", ">", "\\", 0) == (
        "quoted",
        False,
    )
    assert quote.extractwithoutquotes("the 'quoted' part", "'", "'", "\\", 0) == (
        "quoted",
        False,
    )
    assert quote.extractwithoutquotes(
        "the 'isn\\'t escaping fun' part", "'", "'", "\\", 0
    ) == ("isn\\'t escaping fun", False)
    assert quote.extractwithoutquotes("the 'isn\\'t something ", "'", "'", "\\", 0) == (
        "isn\\'t something ",
        True,
    )
    assert quote.extractwithoutquotes("<quoted>\\", "<", ">", "\\", 0) == (
        "quoted",
        False,
    )
    assert quote.extractwithoutquotes("<quoted>\\\\<again>", "<", ">", "\\", 0) == (
        "quotedagain",
        False,
    )
    assert quote.extractwithoutquotes(
        "<quoted><again\\\\", "<", ">", "\\", 0, True
    ) == ("quotedagain\\\\", True)
    # don't include escapes...
    assert quote.extractwithoutquotes(
        "the 'isn\\'t escaping fun' part", "'", "'", "\\", 0, False
    ) == ("isn't escaping fun", False)
    assert quote.extractwithoutquotes(
        "the 'isn\\'t something ", "'", "'", "\\", 0, False
    ) == ("isn't something ", True)
    assert quote.extractwithoutquotes("<quoted\\", "<", ">", "\\", 0, False) == (
        "quoted",
        True,
    )
    assert quote.extractwithoutquotes(
        "<quoted><again\\\\", "<", ">", "\\", 0, False
    ) == ("quotedagain\\", True)
    # escaping of quote char
    assert quote.extractwithoutquotes("<quoted\\>", "<", ">", "\\", 0, False) == (
        "quoted>",
        True,
    )


def isnewlineortabescape(escape):
    if escape in {"\\n", "\\t"}:
        return escape
    return escape[-1]


def test_extractwithoutquotes_passfunc():
    """Tests the extractwithoutquotes function with a function for includeescapes as a parameter."""
    assert quote.extractwithoutquotes(
        "<test \\r \\n \\t \\\\>", "<", ">", "\\", 0, isnewlineortabescape
    ) == ("test r \\n \\t \\", False)


def test_stripcomment():
    assert quote.stripcomment("<!-- Comment -->") == "Comment"


class TestEncoding:
    def test_javapropertiesencode(self):
        assert quote.javapropertiesencode("abc") == "abc"
        assert quote.javapropertiesencode("abcḓ") == r"abc\u1E13"
        assert quote.javapropertiesencode("abc\n") == "abc\\n"

    def test_javapropertiesencode_iso_8859_1(self):
        """Test that ISO-8859-1 characters (0-255) are not encoded."""
        # ASCII characters (0-127) should not be encoded
        assert quote.javapropertiesencode("hello") == "hello"

        # ISO-8859-1 characters (128-255) should not be encoded
        # ú = U+00FA = 250 (in ISO-8859-1)
        assert quote.javapropertiesencode("valú") == "valú"

        # Characters outside ISO-8859-1 (> 255) should be encoded
        # š = U+0161 = 353 (NOT in ISO-8859-1)
        assert quote.javapropertiesencode("Zkouška") == r"Zkou\u0161ka"

        # Mixed test: á, é are in ISO-8859-1, č is not
        # á = U+00E1 = 225, é = U+00E9 = 233, č = U+010D = 269
        assert quote.javapropertiesencode("cáfé") == "cáfé"
        assert quote.javapropertiesencode("čáfé") == r"\u010Dáfé"

    def test_javapropertiesencode_ascii(self):
        """Test that non-ASCII characters are encoded when using ASCII encoding."""
        # ASCII characters (0-127) should not be encoded
        assert quote.javapropertiesencode("hello", encoding="ascii") == "hello"

        # Characters >= 128 should be encoded for ASCII
        # é = U+00E9 = 233 (NOT in ASCII, but in ISO-8859-1)
        assert (
            quote.javapropertiesencode("café", encoding="ascii")
            == r"caf\u00E9"  # codespell:ignore
        )

        # All non-ASCII characters should be encoded
        assert (
            quote.javapropertiesencode("Zkouška", encoding="ascii") == r"Zkou\u0161ka"
        )

    def test_javapropertiesencode_unicode_range(self):
        """Test encoding full unicode range for specifically handled encodings."""
        # Test ASCII encoding - all chars 0-127 should be preserved, rest encoded
        for i in range(256):
            char = chr(i)
            # Add a prefix to avoid the leading space special case
            result = quote.javapropertiesencode("x" + char, encoding="ascii")
            if i < 128 and char not in quote.controlchars:
                # ASCII chars should not be encoded (except control chars)
                assert result == "x" + char, f"ASCII char {i} should not be encoded"
            elif char in quote.controlchars:
                # Control chars have special encoding
                assert result == "x" + quote.controlchars[char]
            else:
                # Non-ASCII should be encoded
                assert result == f"x\\u{i:04X}", (
                    f"Char {i} should be encoded as \\u{i:04X}"
                )

        # Verify ASCII encoded string can be decoded back to bytes in ASCII
        test_str = "hello world"
        encoded = quote.javapropertiesencode(test_str, encoding="ascii")
        assert encoded == test_str
        # Should be valid ASCII bytes
        encoded.encode("ascii")

        # Test ISO-8859-1 encoding - all chars 0-255 should be preserved, rest encoded
        for i in range(512):  # Test beyond 255 to verify encoding
            char = chr(i)
            # Add a prefix to avoid the leading space special case
            result = quote.javapropertiesencode("x" + char, encoding="iso-8859-1")
            if i <= 255 and char not in quote.controlchars:
                # ISO-8859-1 chars should not be encoded
                assert result == "x" + char, (
                    f"ISO-8859-1 char {i} should not be encoded"
                )
            elif char in quote.controlchars:
                # Control chars have special encoding
                assert result == "x" + quote.controlchars[char]
            else:
                # Chars > 255 should be encoded
                assert result == f"x\\u{i:04X}", (
                    f"Char {i} should be encoded as \\u{i:04X}"
                )

        # Verify ISO-8859-1 encoded string can be decoded to bytes in ISO-8859-1
        test_str = "café"  # Contains é (U+00E9 = 233)
        encoded = quote.javapropertiesencode(test_str, encoding="iso-8859-1")
        assert encoded == test_str
        # Should be valid ISO-8859-1 bytes
        encoded.encode("iso-8859-1")

    def test_java_utf8_properties_encode(self):
        assert quote.java_utf8_properties_encode("abc") == "abc"
        assert quote.java_utf8_properties_encode("abcḓ") == "abcḓ"
        assert quote.java_utf8_properties_encode("abc\n") == "abc\\n"

    def test_escapespace(self):
        assert quote.escapespace(" ") == "\\u0020"
        assert quote.escapespace("\t") == "\\u0009"

    def test_mozillaescapemarginspaces(self):
        assert quote.mozillaescapemarginspaces(" ") == r"\u0020"
        assert quote.mozillaescapemarginspaces("A") == "A"
        assert quote.mozillaescapemarginspaces(" abc ") == r"\u0020abc\u0020"
        assert quote.mozillaescapemarginspaces("  abc ") == r"\u0020 abc\u0020"

    def test_mozilla_control_escapes(self):
        r"""Test that we do \uNNNN escapes for certain control characters instead of converting to UTF-8 characters."""
        prefix, suffix = "bling", "blang"
        for control in ("\u0005", "\u0006", "\u0007", "\u0011"):
            string = prefix + control + suffix
            assert quote.escapecontrols(string) != string

    def test_propertiesdecode(self):
        assert quote.propertiesdecode("abc") == "abc"
        assert quote.propertiesdecode("abc\\u1e13") == "abcḓ"
        assert quote.propertiesdecode("abc\\u1E13") == "abcḓ"
        assert quote.propertiesdecode("abc\N{LEFT CURLY BRACKET}") == "abc{"
        assert quote.propertiesdecode("abc\\") == "abc\\"
        assert quote.propertiesdecode("abc\\") == "abc\\"

    def test_controlchars(self):
        assert quote.javapropertiesencode(quote.propertiesdecode("\u0001")) == r"\u0001"
        assert quote.javapropertiesencode(quote.propertiesdecode("\\u01")) == r"\u0001"
        assert quote.javapropertiesencode("\\") == "\\\\"
        assert quote.javapropertiesencode("\x01") == "\\u0001"
        assert quote.propertiesdecode("\x01") == "\x01"
        assert quote.propertiesdecode("\\u0001") == "\x01"

    def test_properties_decode_slashu(self):
        # The real input strings don't have double backslashes, but we have to
        # double them here because Python immediately decode them, even for raw
        # strings.
        assert quote.propertiesdecode("abc\\u1e13") == "abcḓ"
        assert quote.propertiesdecode("abc\\u0020") == "abc "
        # NOTE Java only accepts 4 digit unicode, Mozilla accepts two
        # unfortunately, but it seems harmless to accept both.
        assert quote.propertiesdecode("abc\\u20") == "abc "

    @staticmethod
    def _html_encoding_helper(pairs):
        for from_, to in pairs:
            assert quote.htmlentityencode(from_) == to
            assert quote.htmlentitydecode(to) == from_

    def test_htmlencoding(self):
        """Test that we can encode and decode simple HTML entities."""
        raw_encoded = [("€", "&euro;"), ("©", "&copy;"), ('"', "&quot;")]
        self._html_encoding_helper(raw_encoded)

    def test_htmlencoding_existing_entities(self):
        """Test that we don't mess existing entities."""
        assert quote.htmlentityencode("&amp;") == "&amp;"

    def test_htmlencoding_passthrough(self):
        """Test that we can encode and decode things that look like HTML entities but aren't."""
        raw_encoded = [
            ("copy quot", "copy quot")
        ]  # Raw text should have nothing done to it.
        self._html_encoding_helper(raw_encoded)

    def test_htmlencoding_nonentities(self):
        """Tests to give us full coverage."""
        for encoded, real in [
            ("Some &; text", "Some &; text"),
            ("&copy ", "&copy "),
            ("&copy", "&copy"),
            ("&rogerrabbit;", "&rogerrabbit;"),
        ]:
            assert quote.htmlentitydecode(encoded) == real

        for decoded, real in [
            ("Some &; text", "Some &; text"),
            ("&copy ", "&amp;copy "),
            ("&copy", "&amp;copy"),
            ("&rogerrabbit;", "&rogerrabbit;"),
        ]:
            assert quote.htmlentityencode(decoded) == real
