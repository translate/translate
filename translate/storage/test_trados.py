# -*- coding: utf-8 -*-

from translate.storage import trados_txt as trados


def test_unescape():
    # NBSP
    assert trados.unescape(ur"Ordre du jour\~:") == u"Ordre du jour\u00a0:"
    assert trados.unescape(ur"Association for Road Safety \endash  Conference") == u"Association for Road Safety –  Conference"
