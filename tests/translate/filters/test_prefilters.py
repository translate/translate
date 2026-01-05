"""tests decoration handling functions that are used by checks."""

from translate.filters import prefilters


def test_removekdecomments() -> None:
    assert prefilters.removekdecomments("Some sṱring") == "Some sṱring"
    assert prefilters.removekdecomments("_: Commenṱ\\n\nSome sṱring") == "Some sṱring"
    assert prefilters.removekdecomments("_: Commenṱ\\n\n") == ""


def test_filterwordswithpunctuation() -> None:
    string = "Nothing in here."
    filtered = prefilters.filterwordswithpunctuation(string)
    assert filtered == string
    # test listed words (start / end with apostrophe)
    string = "'n Boom het 'n tak."  # codespell:ignore
    filtered = prefilters.filterwordswithpunctuation(string)
    assert filtered == "n Boom het n tak."  # codespell:ignore
    # test words containing apostrophe
    string = "It's in it's own place."
    filtered = prefilters.filterwordswithpunctuation(string)
    assert filtered == "Its in its own place."
    # test strings in unicode
    string = "Iṱ'š"
    filtered = prefilters.filterwordswithpunctuation(string)
    assert filtered == "Iṱš"
