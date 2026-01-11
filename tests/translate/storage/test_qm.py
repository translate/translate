import pytest

from translate.storage import qm

from . import test_base


class TestQtUnit(test_base.TestTranslationUnit):
    UnitClass = qm.qmunit


class TestQtFile(test_base.TestTranslationStore):
    StoreClass = qm.qmfile

    def test_parse(self) -> None:
        # self.reparse relies on __str__ to be output and then parsed
        # qm.py does not implement serialization
        pass

    def test_save(self) -> None:
        # QM does not implement saving
        with pytest.raises(TypeError):
            self.StoreClass.savefile(self.StoreClass())  # ty:ignore[missing-argument]

    def test_files(self) -> None:
        # QM does not implement saving
        with pytest.raises(TypeError):
            self.StoreClass.savefile(self.StoreClass())  # ty:ignore[missing-argument]

    def test_nonascii(self) -> None:
        # QM does not implement serialising
        with pytest.raises(TypeError):
            self.StoreClass.serialize(self.StoreClass())  # ty:ignore[missing-argument]

    def test_add(self) -> None:
        # QM does not implement serialising
        with pytest.raises(TypeError):
            self.StoreClass.serialize(self.StoreClass())  # ty:ignore[missing-argument]

    def test_remove(self) -> None:
        # QM does not implement serialising
        with pytest.raises(TypeError):
            self.StoreClass.serialize(self.StoreClass())  # ty:ignore[missing-argument]
