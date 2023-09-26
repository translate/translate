from translate.lang import factory


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("tr")
    sentences = language.sentences("Normal case. Nothing interesting.")
    assert sentences == ["Normal case.", "Nothing interesting."]
    sentences = language.sentences("1. sayı, 2. sayı.")
    assert sentences == ["1. sayı, 2. sayı."]
