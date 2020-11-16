from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("th")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg"
    assert language.punctranslate("abc efg. hij") == "abc efg hij"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    # We can forget to do this well without extra help.
    language = factory.getlanguage("th")
    sentences = language.sentences("")
    assert sentences == []
