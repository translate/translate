from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("ko")
    # Nothing should be translated
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("abc efg. hij.") == "abc efg. hij."
    assert language.punctranslate("abc efg!") == "abc efg!"
    assert language.punctranslate("abc efg? hij!") == "abc efg? hij!"
    assert language.punctranslate("Delete file: %s?") == "Delete file: %s?"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("ko")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences("이 연락처에 바뀐 부분이 있습니다. 바뀐 사항을 저장하시겠습니까?")
    print(sentences)
    assert sentences == ["이 연락처에 바뀐 부분이 있습니다.", "바뀐 사항을 저장하시겠습니까?"]
