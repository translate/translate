from translate.storage import utx

from . import test_base


class TestUtxUnit(test_base.TestTranslationUnit):
    UnitClass = utx.UtxUnit


class TestUtxFile(test_base.TestTranslationStore):
    StoreClass = utx.UtxFile
