#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import utx
from translate.storage import test_base


class TestUtxUnit(test_base.TestTranslationUnit):
    UnitClass = utx.UtxUnit


class TestUtxFile(test_base.TestTranslationStore):
    StoreClass = utx.UtxFile
