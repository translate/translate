from pytest import importorskip


trados = importorskip("translate.storage.trados")


def test_unescape():
    # NBSP
    assert trados.unescape("Ordre du jour\\~:") == "Ordre du jour\u00a0:"
    assert (
        trados.unescape("Association for Road Safety \\endash  Conference")
        == "Association for Road Safety –  Conference"
    )


def test_escape():
    # NBSP
    assert trados.escape("Ordre du jour\u00a0:") == "Ordre du jour\\~:"
    assert (
        trados.escape("Association for Road Safety –  Conference")
        == "Association for Road Safety \\endash  Conference"
    )


# @mark.xfail(reason="Lots to implement")
# class TestTradosTxtTmUnit(test_base.TestTranslationUnit):
#    UnitClass = trados.TradosUnit
#
# @mark.xfail(reason="Lots to implement")
# class TestTrodosTxtTmFile(test_base.TestTranslationStore):
#    StoreClass = trados.TradosTxtTmFile
