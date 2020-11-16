from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("vi")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("abc efg!") == "abc efg !"
    assert language.punctranslate("abc efg? hij!") == "abc efg? hij !"
    assert language.punctranslate("Delete file: %s?") == "Delete file : %s?"
    assert language.punctranslate('The user "root"') == "The user «\u00a0root\u00a0»"
    # More exhaustive testing of the quoting is in test_fr.py
    assert language.punctranslate('Lưu "Tập tin"') == "Lưu «\u00a0Tập tin\u00a0»"
    assert language.punctranslate("Lưu 'Tập tin'") == "Lưu «\u00a0Tập tin\u00a0»"
    assert language.punctranslate("Lưu `Tập tin'") == "Lưu «\u00a0Tập tin\u00a0»"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("vi")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences("Normal case. Nothing interesting.")
    assert sentences == ["Normal case.", "Nothing interesting."]
    sentences = language.sentences("Is that the case ? Sounds interesting !")
    assert sentences == ["Is that the case ?", "Sounds interesting !"]
