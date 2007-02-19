#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import factory

def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage('km')
    assert language.punctranslate(u"abc efg") == u"abc efg"
    assert language.punctranslate(u"abc efg.") == u"abc efg\u00a0។"
    print language.punctranslate(u"abc efg. hij.").encode('utf-8')
    print u"abc efg\u00a0។ hij\u00a0។".encode('utf-8')
    assert language.punctranslate(u"abc efg. hij.") == u"abc efg\u00a0។ hij\u00a0។"
    assert language.punctranslate(u"abc efg!") == u"abc efg\u00a0!"
    assert language.punctranslate(u"abc efg? hij!") == u"abc efg\u00a0? hij\u00a0!"
    assert language.punctranslate(u"Delete file: %s?") == u"Delete file\u00a0៖ %s\u00a0?"

