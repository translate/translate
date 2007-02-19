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

