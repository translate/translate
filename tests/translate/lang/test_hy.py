from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("hy")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg։"
    assert language.punctranslate("abc efg. hij.") == "abc efg։ hij։"
    assert language.punctranslate("abc efg!") == "abc efg՜"
    assert language.punctranslate("Delete file: %s") == "Delete file՝ %s"
    # TODO: Find out exactly how questions work


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("hy")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "Արխիվն արդեն գոյություն ունի։ Դուք ցանկանու՞մ եք կրկին գրել այն։"
    )
    assert sentences == [
        "Արխիվն արդեն գոյություն ունի։",
        "Դուք ցանկանու՞մ եք կրկին գրել այն։",
    ]
    sentences = language.sentences(
        "Արխիվն արդեն գոյություն ունի։ դուք ցանկանու՞մ եք կրկին գրել այն։"
    )
    assert sentences == [
        "Արխիվն արդեն գոյություն ունի։ դուք ցանկանու՞մ եք կրկին գրել այն։"
    ]
