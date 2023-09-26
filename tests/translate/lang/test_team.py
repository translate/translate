from translate.lang.team import guess_language


def test_simple():
    """
    test the regex, team snippet and language name snippets at a high
    level
    """
    # standard regex guess
    assert guess_language("ab@li.org") == "ab"
    # We never suggest 'en', it's always a mistake
    assert guess_language("en@li.org") is None
    # We can't have a single char language code
    assert guess_language("C@li.org") is None
    # Testing regex postfilter
    assert guess_language("LL@li.org") is None

    # snippet guess based on contact info
    assert guess_language("assam@mm.assam-glug.org") == "as"
    # snippet guess based on a language name
    assert guess_language("Hawaiian") == "haw"

    # We found nothing
    assert guess_language("Bork bork") is None
