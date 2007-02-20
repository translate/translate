#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import factory

def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage('af')
    sentences = language.sentences(u"Normal case. Nothing interesting.")
    assert sentences == [u"Normal case.", "Nothing interesting."]
    sentences = language.sentences(u"Wat? 'n Fout?")
    assert sentences == [u"Wat?", "'n Fout?"]
