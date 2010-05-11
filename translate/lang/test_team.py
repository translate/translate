#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang.team import guess_language


def test_simple():
    """test the regex, team snippet and language name snippets at a high
    level"""
    assert guess_language("ab@li.org") == "ab"
    assert guess_language("en@li.org") == None
    assert guess_language("C@li.org") == None
    assert guess_language("assam@mm.assam-glug.org") == "as"
    assert guess_language("Hawaiian") == "haw"
    assert guess_language("Bork bork") is None
