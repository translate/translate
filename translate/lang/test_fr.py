from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("fr")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("abc efg!") == "abc efg\u00a0!"
    assert language.punctranslate("abc efg? hij!") == "abc efg\u00a0? hij\u00a0!"
    assert language.punctranslate("Delete file: %s?") == "Delete file\u00a0: %s\u00a0?"
    assert (
        language.punctranslate('"root" is powerful') == "«\u00a0root\u00a0» is powerful"
    )
    assert (
        language.punctranslate("'root' is powerful") == "«\u00a0root\u00a0» is powerful"
    )
    assert (
        language.punctranslate("`root' is powerful") == "«\u00a0root\u00a0» is powerful"
    )
    assert language.punctranslate('The user "root"') == "The user «\u00a0root\u00a0»"
    assert language.punctranslate("The user 'root'") == "The user «\u00a0root\u00a0»"
    assert language.punctranslate("The user `root'") == "The user «\u00a0root\u00a0»"
    assert (
        language.punctranslate('The user "root"?')
        == "The user «\u00a0root\u00a0»\u00a0?"
    )
    assert (
        language.punctranslate("The user 'root'?")
        == "The user «\u00a0root\u00a0»\u00a0?"
    )
    assert (
        language.punctranslate("The user `root'?")
        == "The user «\u00a0root\u00a0»\u00a0?"
    )
    assert language.punctranslate('Watch the " mark') == 'Watch the " mark'
    assert language.punctranslate("Watch the ' mark") == "Watch the ' mark"
    assert language.punctranslate("Watch the ` mark") == "Watch the ` mark"
    assert language.punctranslate("Watch the “mark”") == "Watch the «\u00a0mark\u00a0»"
    assert (
        language.punctranslate('The <a href="info">user</a> "root"?')
        == 'The <a href="info">user</a> «\u00a0root\u00a0»\u00a0?'
    )
    assert (
        language.punctranslate("The <a href='info'>user</a> 'root'?")
        == "The <a href='info'>user</a> «\u00a0root\u00a0»\u00a0?"
    )
    # Broken because we test for equal number of ` and ' in the string
    # assert language.punctranslate("The <a href='info'>user</a> `root'?") == "The <a href='info'>user</a> «\u00a0root\u00a0»\u00a0?"
    assert (
        language.punctranslate("The <a href='http://koeie'>user</a>")
        == "The <a href='http://koeie'>user</a>"
    )

    assert (
        language.punctranslate("Copying `%s' to `%s'")
        == "Copying «\u00a0%s\u00a0» to «\u00a0%s\u00a0»"
    )


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("fr")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences("Normal case. Nothing interesting.")
    assert sentences == ["Normal case.", "Nothing interesting."]
    sentences = language.sentences("Is that the case ? Sounds interesting !")
    assert sentences == ["Is that the case ?", "Sounds interesting !"]
