from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("ja")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg。"
    assert language.punctranslate("(abc efg).") == "(abc efg)。"
    assert language.punctranslate("(abc efg). hijk") == "(abc efg)。hijk"
    assert language.punctranslate(".") == "。"
    assert language.punctranslate("abc efg...") == "abc efg..."


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("ja")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences("明日は、明日の風が吹く。吾輩は猫である。\n")
    assert sentences == ["明日は、明日の風が吹く。", "吾輩は猫である。"]
    sentences = language.sentences("頑張れ！甲子園に行きたいか？")
    assert sentences == ["頑張れ！", "甲子園に行きたいか？"]
