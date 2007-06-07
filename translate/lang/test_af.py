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

def test_capsstart():
    """Tests that the indefinite article ('n) doesn't confuse startcaps()."""
    language = factory.getlanguage('af')
    assert language.capsstart("Koeie kraam koeie")
    assert language.capsstart("'Koeie' kraam koeie")
    assert not language.capsstart("koeie kraam koeie")
    assert language.capsstart("'n Koei kraam koeie")
    assert language.capsstart("'n 'Koei' kraam koeie")
    assert not language.capsstart("'n oei kraam koeie")

