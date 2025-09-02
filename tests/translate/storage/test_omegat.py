from pytest import mark

from translate.storage import omegat

from . import test_base


class TestOmegaTUnit(test_base.TestTranslationUnit):
    UnitClass = omegat.OmegaTUnit


class TestOmegaTFile(test_base.TestTranslationStore):
    StoreClass = omegat.OmegaTFile

    @mark.xfail(
        reason="This doesn't work, due to two store classes handling different "
        "extensions, but factory listing it as one supported file type"
    )
    def test_extensions(self):
        super().test_extensions()
