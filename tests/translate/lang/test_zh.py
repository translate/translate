from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("zh")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg。"
    assert language.punctranslate("(abc efg).") == "(abc efg)。"
    assert language.punctranslate("(abc efg). hijk") == "(abc efg)。hijk"
    assert language.punctranslate(".") == "。"
    assert language.punctranslate("abc efg...") == "abc efg..."


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("zh")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences("這個用戶名稱已經存在。現在會寄一封信給已登記的電郵地址。\n")
    assert sentences == ["這個用戶名稱已經存在。", "現在會寄一封信給已登記的電郵地址。"]
