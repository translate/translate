#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import common

def test_words():
    """Tests basic functionality of word segmentation."""
    language = common.Common
    words = language.words(u"Test sentence.")
    assert words == [u"Test", u"sentence"]

    # Let's test Khmer with zero width space (\u200b)
    words = language.words(u"ផ្ដល់​យោបល់")
    assert words == [u"ផ្ដល់", u"យោបល់"]

    words = language.words(u"This is a weird test .")
    assert words == [u"This", u"is", u"a", u"weird", u"test"]

def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = common.Common
    sentences = language.sentences(u"This is a sentence.")
    assert sentences == [u"This is a sentence."]
    sentences = language.sentences(u"This is a sentence")
    assert sentences == [u"This is a sentence"]
    sentences = language.sentences(u"This is a sentence. Another one.")
    assert sentences == [u"This is a sentence.", "Another one."]
    sentences = language.sentences(u"This is a sentence. Another one. Bla.")
    assert sentences == [u"This is a sentence.", "Another one.", "Bla."]
    sentences = language.sentences(u"This is a sentence.Not another one.")
    assert sentences == [u"This is a sentence.Not another one."]
    sentences = language.sentences(u"Exclamation! Really? No...")
    assert sentences == [u"Exclamation!", "Really?", "No..."]
    sentences = language.sentences(u"Four i.e. 1+3. See?")
    assert sentences == [u"Four i.e. 1+3.", "See?"]
    sentences = language.sentences(u"Apples, bananas, etc. are nice.")
    assert sentences == [u"Apples, bananas, etc. are nice."]
    sentences = language.sentences(u"Apples, bananas, etc.\nNext part")
    assert sentences == [u"Apples, bananas, etc.", "Next part"]

