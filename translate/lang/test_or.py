from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("or")
    assert language.punctranslate("") == ""
    assert language.punctranslate("Document loaded") == "Document loaded"
    assert language.punctranslate("Document loaded.") == "Document loaded।"
    assert language.punctranslate("Document loaded.\n") == "Document loaded।\n"
    assert language.punctranslate("Document loaded...") == "Document loaded..."


def test_country_code():
    """
    Tests that we get the correct one even if a country code is attached to
    a special code being a reserved word in Python (like 'or').
    """
    language = factory.getlanguage("or-IN")
    assert language.fullname == "Odia"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("or")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "ଗୋଟିଏ ଚାବିକୁ ଆଲୋକପାତ କରିବା ପାଇଁ ମାଉସ ସୂଚକକୁ ତାହା ଉପରକୁ ଘୁଞ୍ଚାନ୍ତୁ। ଚୟନ କରିବା ପାଇଁ ଗୋଟିଏ ସୁଇଚକୁ ଦବାନ୍ତୁ।"
    )
    assert sentences == [
        "ଗୋଟିଏ ଚାବିକୁ ଆଲୋକପାତ କରିବା ପାଇଁ ମାଉସ ସୂଚକକୁ ତାହା ଉପରକୁ ଘୁଞ୍ଚାନ୍ତୁ।",
        "ଚୟନ କରିବା ପାଇଁ ଗୋଟିଏ ସୁଇଚକୁ ଦବାନ୍ତୁ।",
    ]
