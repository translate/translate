from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("es")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("abc efg?") == "¿abc efg?"
    assert language.punctranslate("abc efg!") == "¡abc efg!"
    # We have to be a bit more gentle on the code by using capitals correctly.
    # Can we be more robust with this witout affecting sentence segmentation?
    assert language.punctranslate("Abc efg? Hij.") == "¿Abc efg? Hij."
    assert language.punctranslate("Abc efg! Hij.") == "¡Abc efg! Hij."
    # TODO: we should be doing better, but at the only we only support the first sentence


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("es")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "El archivo <b>%1</b> ha sido modificado. ¿Desea guardarlo?"
    )
    print(sentences)
    assert sentences == [
        "El archivo <b>%1</b> ha sido modificado.",
        "¿Desea guardarlo?",
    ]
