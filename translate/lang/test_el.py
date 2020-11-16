from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("el")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg. hij.") == "abc efg. hij."
    assert language.punctranslate("abc efg;") == "abc efg·"
    assert language.punctranslate("abc efg? hij!") == "abc efg; hij!"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("el")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "Θέλετε να αποθηκεύσετε το παιχνίδι σας; (Θα σβησθούν οι Αυτόματες-Αποθηκεύσεις)"
    )
    assert sentences == [
        "Θέλετε να αποθηκεύσετε το παιχνίδι σας;",
        "(Θα σβησθούν οι Αυτόματες-Αποθηκεύσεις)",
    ]
    sentences = language.sentences("Πρώτη πρόταση. Δεύτερη πρόταση.")
    assert sentences == ["Πρώτη πρόταση.", "Δεύτερη πρόταση."]
    sentences = language.sentences("Πρώτη πρόταση. δεύτερη πρόταση.")
    assert sentences == ["Πρώτη πρόταση. δεύτερη πρόταση."]
