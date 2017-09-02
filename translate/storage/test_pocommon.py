# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from translate.storage import pocommon


def test_roundtrip_quote_plus():
    "Test that what we put in is what we get out"""
    def roundtrip_quote_plus(text, quoted):
        quote = pocommon.quote_plus(text)
        assert quote == quoted
        unquote = pocommon.unquote_plus(quoted)
        assert unquote == text
    roundtrip_quote_plus("abc", "abc")
    roundtrip_quote_plus("key space", "key+space")
    roundtrip_quote_plus("key ḓey", "key+%E1%B8%93ey")
    roundtrip_quote_plus(
        "path/file.c(2):3,path space/file.h:4",
        "path/file.c(2):3,path+space/file.h:4"
    )
