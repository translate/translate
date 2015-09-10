# -*- coding: utf-8 -*-

from translate.lang import factory


def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage('ja')
    assert language.punctranslate(u"") == u""
    assert language.punctranslate(u"abc efg") == u"abc efg"
    assert language.punctranslate(u"abc efg.") == u"abc efg。"
    assert language.punctranslate(u"(abc efg).") == u"(abc efg)。"
    assert language.punctranslate(u"(abc efg). hijk") == u"(abc efg)。hijk"
    assert language.punctranslate(u".") == u"。"
    assert language.punctranslate(u"abc efg...") == u"abc efg..."


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage('ja')
    sentences = language.sentences(u"")
    assert sentences == []

    sentences = language.sentences(u"明日は、明日の風が吹く。吾輩は猫である。\n")
    assert sentences == [u"明日は、明日の風が吹く。", u"吾輩は猫である。"]
    sentences = language.sentences(u"頑張れ！甲子園に行きたいか？")
    assert sentences == [u"頑張れ！", u"甲子園に行きたいか？"]
