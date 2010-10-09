# -*- coding: utf-8 -*-

from py.test import mark

from translate.storage import test_base
from translate.storage import trados


def test_unescape():
    # NBSP
    assert trados.unescape(ur"Ordre du jour\~:") == u"Ordre du jour\u00a0:"
    assert trados.unescape(ur"Association for Road Safety \endash  Conference") == u"Association for Road Safety –  Conference"

#@mark.xfail(reason="Lots to implement")
#class TestTradosTxtTmUnit(test_base.TestTranslationUnit):
#    UnitClass = trados.TradosUnit
#
#@mark.xfail(reason="Lots to implement")
#class TestTrodosTxtTmFile(test_base.TestTranslationStore):
#    StoreClass = trados.TradosTxtTmFile
