from translate.storage import test_base, utx


class TestUtxUnit(test_base.TestTranslationUnit):
    UnitClass = utx.UtxUnit


class TestUtxFile(test_base.TestTranslationStore):
    StoreClass = utx.UtxFile
