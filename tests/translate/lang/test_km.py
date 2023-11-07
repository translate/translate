from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("km")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg\u00a0។"
    print(language.punctranslate("abc efg. hij.").encode("utf-8"))
    print("abc efg\u00a0។ hij\u00a0។".encode())
    assert language.punctranslate("abc efg. hij.") == "abc efg\u00a0។ hij\u00a0។"
    assert language.punctranslate("abc efg!") == "abc efg\u00a0!"
    assert language.punctranslate("abc efg? hij!") == "abc efg\u00a0? hij\u00a0!"
    assert language.punctranslate("Delete file: %s?") == "Delete file\u00a0៖ %s\u00a0?"


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("km")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "លក្ខណៈ\u200b\u200bនេះ\u200bអាច\u200bឲ្យ\u200bយើងធ្វើ\u200bជាតូបនីយកម្មកម្មវិធី\u200bកុំព្យូទ័រ\u200b ។ លក្ខណៈ\u200b\u200bនេះ\u200bអាច\u200bឲ្យ\u200bយើងធ្វើ\u200bជាតូបនីយកម្មកម្មវិធី\u200bកុំព្យូទ័រ\u200b ។"
    )
    print(sentences)
    assert sentences == [
        "លក្ខណៈ\u200b\u200bនេះ\u200bអាច\u200bឲ្យ\u200bយើងធ្វើ\u200bជាតូបនីយកម្មកម្មវិធី\u200bកុំព្យូទ័រ\u200b ។",
        "លក្ខណៈ\u200b\u200bនេះ\u200bអាច\u200bឲ្យ\u200bយើងធ្វើ\u200bជាតូបនីយកម្មកម្មវិធី\u200bកុំព្យូទ័រ\u200b ។",
    ]
