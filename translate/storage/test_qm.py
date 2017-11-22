# -*- coding: utf-8 -*-

import pytest

from translate.storage import qm, test_base


class TestQtUnit(test_base.TestTranslationUnit):
    UnitClass = qm.qmunit


class TestQtFile(test_base.TestTranslationStore):
    StoreClass = qm.qmfile

    def test_parse(self):
        # self.reparse relies on __str__ to be output and then parsed
        # qm.py does not implement serialization
        pass

    def test_save(self):
        # QM does not implement saving
        with pytest.raises(Exception):
            self.StoreClass.savefile(self.StoreClass())

    def test_files(self):
        # QM does not implement saving
        with pytest.raises(Exception):
            self.StoreClass.savefile(self.StoreClass())

    def test_nonascii(self):
        # QM does not implement serialising
        with pytest.raises(Exception):
            self.StoreClass.serialize(self.StoreClass())

    def test_add(self):
        # QM does not implement serialising
        with pytest.raises(Exception):
            self.StoreClass.serialize(self.StoreClass())
