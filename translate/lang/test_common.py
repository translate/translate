from pytest import mark

from translate.lang import common


def test_characters():
    """Test the basic characters segmentation"""
    language = common.Common
    assert language.characters("") == []
    assert language.characters("Four") == ["F", "o", "u", "r"]
    assert language.characters("A B") == ["A", " ", "B"]
    # Spaces are compacted, source has 2 returned has only one
    assert language.characters("A  B") == ["A", " ", "B"]


def test_words():
    """Tests basic functionality of word segmentation."""
    language = common.Common
    words = language.words("")
    assert words == []

    words = language.words("test sentence.")
    assert words == ["test", "sentence"]

    words = language.words("This is a weird test .")
    assert words == ["This", "is", "a", "weird", "test"]

    words = language.words("Don't send e-mail!")
    assert words == ["Don't", "send", "e-mail"]

    words = language.words("Don’t send e-mail!")
    assert words == ["Don’t", "send", "e-mail"]


@mark.xfail(
    reason="ZWS is not considered a space in Python 2.6+. Khmer "
    "should extend words() to include \\u200b in addition to "
    "other word breakers."
)
def test_word_khmer():
    language = common.Common
    # Let's test Khmer with zero width space (\u200b)
    words = language.words("ផ្ដល់​យោបល់")
    print("ផ្ដល់​យោបល់")
    print(language.words("ផ្ដល់<200b>យោបល់"))
    print(["ផ្ដល់", "យោបល់"])
    assert words == ["ផ្ដល់", "យោបល់"]


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = common.Common
    # Check that we correctly handle an empty string:
    sentences = language.sentences("")

    sentences = language.sentences("This is a sentence.")
    assert sentences == ["This is a sentence."]
    sentences = language.sentences("This is a sentence")
    assert sentences == ["This is a sentence"]
    sentences = language.sentences("This is a sentence. Another one.")
    assert sentences == ["This is a sentence.", "Another one."]
    sentences = language.sentences("This is a sentence. Another one. Bla.")
    assert sentences == ["This is a sentence.", "Another one.", "Bla."]
    sentences = language.sentences("This is a sentence.Not another one.")
    assert sentences == ["This is a sentence.Not another one."]
    sentences = language.sentences("Exclamation! Really? No...")
    assert sentences == ["Exclamation!", "Really?", "No..."]
    sentences = language.sentences("Four i.e. 1+3. See?")
    assert sentences == ["Four i.e. 1+3.", "See?"]
    sentences = language.sentences("Apples, bananas, etc. are nice.")
    assert sentences == ["Apples, bananas, etc. are nice."]
    sentences = language.sentences("Apples, bananas, etc.\nNext part")
    assert sentences == ["Apples, bananas, etc.", "Next part"]
    sentences = language.sentences(
        "No font for displaying text in encoding '%s' found,\nbut an alternative encoding '%s' is available.\nDo you want to use this encoding (otherwise you will have to choose another one)?"
    )
    assert sentences == [
        "No font for displaying text in encoding '%s' found,\nbut an alternative encoding '%s' is available.",
        "Do you want to use this encoding (otherwise you will have to choose another one)?",
    ]
    # Test that a newline at the end won't confuse us
    sentences = language.sentences("The first sentence. The second sentence.\n")
    assert sentences == ["The first sentence.", "The second sentence."]
    sentences = language.sentences("P.O. box")
    assert sentences == ["P.O. box"]
    sentences = language.sentences("Doen dit d.m.v. koeie.")
    assert sentences == ["Doen dit d.m.v. koeie."]


def test_capsstart():
    """Tests for basic sane behaviour in startcaps()."""
    language = common.Common
    assert language.capsstart("Open cow file")
    assert language.capsstart("'Open' cow file")
    assert not language.capsstart("open cow file")
    assert not language.capsstart(":")
    assert not language.capsstart("")


def test_numstart():
    """Tests for basic sane behaviour in startcaps()."""
    language = common.Common
    assert language.numstart("360 degress")
    assert language.numstart("3D file")
    assert not language.numstart("Open 360 degrees")
    assert not language.numstart(":")
    assert not language.numstart("")


def test_punctranslate():
    """Test the basic punctranslate function"""
    language = common.Common
    assert not language.punctranslate("A...") == "A…"
    language.puncdict = {"...": "…"}
    assert language.punctranslate("A...") == "A…"


def test_length_difference():
    """Test the heuristics of the length difference function"""
    # Expansion with no code
    assert common.Common.length_difference(10) == 6
    assert common.Common.length_difference(100) == 15
    assert common.Common.length_difference(300) == 35


def test_alter_length():
    """Test that we create the correct length by adding or removing characters"""
    assert common.Common.alter_length("One two three") == "One twOne two three"
