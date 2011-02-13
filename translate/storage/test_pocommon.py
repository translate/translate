#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import pocommon


def test_roundtrip_quote_plus():
    "Test that what we put in is what we get out"""
    def roundtrip_quote_plus(text):
        quote = pocommon.quote_plus(text)
        unquote = pocommon.unquote_plus(quote)
        assert unquote == text
    roundtrip_quote_plus("abc")
    roundtrip_quote_plus("key space")
    roundtrip_quote_plus(u"key ḓey")


def test_quote_escapes():
    """Test the specific characters that we want to escape"""
    assert pocommon.quote_plus("space space") == "space+space"
