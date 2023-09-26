from translate.lang import factory


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("uk")
    sentences = language.sentences("")
    assert sentences == []
    sentences = language.sentences("Ел. пошта")
    assert sentences == ["Ел. пошта"]
