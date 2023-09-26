from translate.misc import quote


def test_find_all():
    """tests the find_all function"""
    assert quote.find_all("", "a") == []
    assert quote.find_all("a", "b") == []
    assert quote.find_all("a", "a") == [0]
    assert quote.find_all("aa", "a") == [0, 1]
    assert quote.find_all("abba", "ba") == [2]
    # check we skip the whole instance
    assert quote.find_all("banana", "ana") == [1]


def test_extract():
    """tests the extract function"""
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
    """tests the extractwithoutquotes function"""
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
    if escape in ("\\n", "\\t"):
        return escape
    return escape[-1]


def test_extractwithoutquotes_passfunc():
    """tests the extractwithoutquotes function with a function for includeescapes as a parameter"""
    assert quote.extractwithoutquotes(
        "<test \\r \\n \\t \\\\>", "<", ">", "\\", 0, isnewlineortabescape
    ) == ("test r \\n \\t \\", False)


def test_stripcomment():
    assert quote.stripcomment("<!-- Comment -->") == "Comment"


class TestEncoding:
    @staticmethod
    def test_javapropertiesencode():
        assert quote.javapropertiesencode("abc") == "abc"
        assert quote.javapropertiesencode("abcḓ") == r"abc\u1E13"
        assert quote.javapropertiesencode("abc\n") == "abc\\n"

    @staticmethod
    def test_java_utf8_properties_encode():
        assert quote.java_utf8_properties_encode("abc") == "abc"
        assert quote.java_utf8_properties_encode("abcḓ") == "abcḓ"
        assert quote.java_utf8_properties_encode("abc\n") == "abc\\n"

    @staticmethod
    def test_escapespace():
        assert quote.escapespace(" ") == "\\u0020"
        assert quote.escapespace("\t") == "\\u0009"

    @staticmethod
    def test_mozillaescapemarginspaces():
        assert quote.mozillaescapemarginspaces(" ") == ""
        assert quote.mozillaescapemarginspaces("A") == "A"
        assert quote.mozillaescapemarginspaces(" abc ") == "\\u0020abc\\u0020"
        assert quote.mozillaescapemarginspaces("  abc ") == "\\u0020 abc\\u0020"

    @staticmethod
    def test_mozilla_control_escapes():
        r"""test that we do \uNNNN escapes for certain control characters instead of converting to UTF-8 characters"""
        prefix, suffix = "bling", "blang"
        for control in ("\u0005", "\u0006", "\u0007", "\u0011"):
            string = prefix + control + suffix
            assert quote.escapecontrols(string) == string

    @staticmethod
    def test_propertiesdecode():
        assert quote.propertiesdecode("abc") == "abc"
        assert quote.propertiesdecode("abc\\u1e13") == "abcḓ"
        assert quote.propertiesdecode("abc\\u1E13") == "abcḓ"
        assert quote.propertiesdecode("abc\N{LEFT CURLY BRACKET}") == "abc{"
        assert quote.propertiesdecode("abc\\") == "abc\\"
        assert quote.propertiesdecode("abc\\") == "abc\\"

    @staticmethod
    def test_properties_decode_slashu():
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
        """test that we can encode and decode simple HTML entities"""
        raw_encoded = [("€", "&euro;"), ("©", "&copy;"), ('"', "&quot;")]
        self._html_encoding_helper(raw_encoded)

    @staticmethod
    def test_htmlencoding_existing_entities():
        """test that we don't mess existing entities"""
        assert quote.htmlentityencode("&amp;") == "&amp;"

    def test_htmlencoding_passthrough(self):
        """test that we can encode and decode things that look like HTML entities but aren't"""
        raw_encoded = [
            ("copy quot", "copy quot")
        ]  # Raw text should have nothing done to it.
        self._html_encoding_helper(raw_encoded)

    @staticmethod
    def test_htmlencoding_nonentities():
        """tests to give us full coverage"""
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
