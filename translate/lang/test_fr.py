#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import factory

def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage('fr')
    assert language.punctranslate(u"abc efg") == u"abc efg"
    assert language.punctranslate(u"abc efg.") == u"abc efg."
    assert language.punctranslate(u"abc efg!") == u"abc efg !"
    assert language.punctranslate(u"abc efg? hij!") == u"abc efg ? hij !"
    assert language.punctranslate(u"Delete file: %s?") == u"Delete file : %s ?"
    assert language.punctranslate(u'The user "root"') == u"The user « root »"
