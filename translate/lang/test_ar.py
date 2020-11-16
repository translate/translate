from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("ar")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("abc, efg; d?") == "abc، efg؛ d؟"
    # See https://github.com/translate/translate/issues/1819
    assert language.punctranslate("It is called “abc”") == "It is called ”abc“"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("ar")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences('يوجد بالفعل مجلد بالإسم "%s". أترغب في استبداله؟')
    print(sentences)
    assert sentences == ['يوجد بالفعل مجلد بالإسم "%s".', "أترغب في استبداله؟"]
    # This probably doesn't make sense: it is just the above reversed, to make sure
    # we test the '؟' as an end of sentence marker.
    sentences = language.sentences('أترغب في استبداله؟ يوجد بالفعل مجلد بالإسم "%s".')
    print(sentences)
    assert sentences == ["أترغب في استبداله؟", 'يوجد بالفعل مجلد بالإسم "%s".']
