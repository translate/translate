from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("am")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg።"
    assert language.punctranslate("abc efg. hij.") == "abc efg። hij።"
    assert language.punctranslate("abc efg, hij;") == "abc efg፣ hij፤"
    assert language.punctranslate("Delete file: %s?") == "Delete file: %s?"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("am")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "ለምልክቱ መግቢያ የተለየ መለያ። ይህ የሚጠቅመው የታሪኩን ዝርዝር ለማስቀመጥ ነው።"
    )
    print(sentences)
    assert sentences == ["ለምልክቱ መግቢያ የተለየ መለያ።", "ይህ የሚጠቅመው የታሪኩን ዝርዝር ለማስቀመጥ ነው።"]
