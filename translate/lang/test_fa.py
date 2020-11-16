from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("fa")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("Delete file: %s?") == "Delete file: %s؟"
    assert language.punctranslate('"root" is powerful') == "«root» is powerful"
    assert language.punctranslate("'root' is powerful") == "«root» is powerful"
    assert language.punctranslate("`root' is powerful") == "«root» is powerful"
    assert language.punctranslate('The user "root"') == "The user «root»"
    assert language.punctranslate("The user 'root'") == "The user «root»"
    assert language.punctranslate("The user `root'") == "The user «root»"
    assert language.punctranslate('The user "root"?') == "The user «root»؟"
    assert language.punctranslate("The user 'root'?") == "The user «root»؟"
    assert language.punctranslate("The user `root'?") == "The user «root»؟"
    assert language.punctranslate('Watch the " mark') == 'Watch the " mark'
    assert language.punctranslate("Watch the ' mark") == "Watch the ' mark"
    assert language.punctranslate("Watch the ` mark") == "Watch the ` mark"
    assert language.punctranslate("Watch the “mark”") == "Watch the «mark»"
    assert (
        language.punctranslate('The <a href="info">user</a> "root"?')
        == 'The <a href="info">user</a> «root»؟'
    )
    assert (
        language.punctranslate("The <a href='info'>user</a> 'root'?")
        == "The <a href='info'>user</a> «root»؟"
    )
    # Broken because we test for equal number of ` and ' in the string
    # assert language.punctranslate("The <a href='info'>user</a> `root'?") == "The <a href='info'>user</a> «root»؟"
    assert (
        language.punctranslate("The <a href='http://koeie'>user</a>")
        == "The <a href='http://koeie'>user</a>"
    )

    assert language.punctranslate("Copying `%s' to `%s'") == "Copying «%s» to «%s»"
    # We are very careful by checking that the ` and ' match, so we miss this because of internal punctuation:
    # assert language.punctranslate("Shlib `%s' didn't contain `%s'") == "Shlib «%s» didn't contain «%s»"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("fa")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences("Normal case. Nothing interesting.")
    assert sentences == ["Normal case.", "Nothing interesting."]
    sentences = language.sentences("Is that the case ? Sounds interesting !")
    assert sentences == ["Is that the case ?", "Sounds interesting !"]
