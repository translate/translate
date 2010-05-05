#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import test_base
from translate.storage import qm

from py import test


class TestOtUnit(test_base.TestTranslationUnit):
    UnitClass = qm.qmunit


class TestOtFile(test_base.TestTranslationStore):
    StoreClass = qm.qmfile

    def test_parse(self):
        # self.reparse relies on __str__ to be output and then parsed
        # qm.py does not implement __str__ but returns u''
        pass

    def test_save(self):
        # QM does not implement saving
        assert test.raises(Exception, self.StoreClass.savefile,
                           self.StoreClass())

    def test_files(self):
        # QM does not implement saving
        assert test.raises(Exception, self.StoreClass.savefile,
                           self.StoreClass())
