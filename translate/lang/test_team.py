#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang.team import guess_language


def test_simple():
    """test the regex, team snippet and language name snippets at a high
    level"""
    assert guess_language(u"ab@li.org") == "ab"
    assert guess_language(u"en@li.org") == None
    assert guess_language(u"C@li.org") == None
    assert guess_language(u"assam@mm.assam-glug.org") == "as"
    assert guess_language(u"Hawaiian") == "haw"
    assert guess_language(u"Bork bork") is None
