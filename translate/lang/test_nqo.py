from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("nqo")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg."
    assert language.punctranslate("abc efg!") == "abc efg߹"
    assert language.punctranslate("abc, efg; d?") == "abc߸ efg؛ d؟"
    # See https://github.com/translate/translate/issues/1819
    assert language.punctranslate("It is called “abc”") == "It is called ”abc“"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("nqo")
    sentences = language.sentences("")
    assert sentences == []

    # this text probably does not make sense, I just copied it from Firefox
    # translation and added some punctuation marks
    sentences = language.sentences(
        "ߡߍ߲ ߠߎ߬ ߦߋ߫ ߓߊ߯ߙߊ߫ ߟߊ߫ ߢߐ߲߮ ߝߍ߬ ߞߊ߬ ߓߟߐߟߐ ߟߊߞߊ߬ߣߍ߲ ߕߏ߫. ߖߊ߬ߡߊ ߣߌ߫ ߓߍ߯ ߛߊ߬ߥߏ ߘߐ߫."
    )
    print(sentences)
    assert sentences == [
        "ߡߍ߲ ߠߎ߬ ߦߋ߫ ߓߊ߯ߙߊ߫ ߟߊ߫ ߢߐ߲߮ ߝߍ߬ ߞߊ߬ ߓߟߐߟߐ ߟߊߞߊ߬ߣߍ߲ ߕߏ߫.",
        "ߖߊ߬ߡߊ ߣߌ߫ ߓߍ߯ ߛߊ߬ߥߏ ߘߐ߫.",
    ]
    sentences = language.sentences(
        "ߡߍ߲ ߠߎ߬ ߦߋ߫ ߓߊ߯ߙߊ߫ ߟߊ߫ ߢߐ߲߮ ߝߍ߬ ߞߊ߬ ߓߟߐߟߐ ߟߊߞߊ߬ߣߍ߲ ߕߏ߫? ߖߊ߬ߡߊ ߣߌ߫ ߓߍ߯ ߛߊ߬ߥߏ ߘߐ߫."
    )
    print(sentences)
    assert sentences == [
        "ߡߍ߲ ߠߎ߬ ߦߋ߫ ߓߊ߯ߙߊ߫ ߟߊ߫ ߢߐ߲߮ ߝߍ߬ ߞߊ߬ ߓߟߐߟߐ ߟߊߞߊ߬ߣߍ߲ ߕߏ߫?",
        "ߖߊ߬ߡߊ ߣߌ߫ ߓߍ߯ ߛߊ߬ߥߏ ߘߐ߫.",
    ]
