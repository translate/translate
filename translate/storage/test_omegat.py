#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import test_base
from translate.storage import omegat as ot


class TestOtUnit(test_base.TestTranslationUnit):
    UnitClass = ot.OmegaTUnit


class TestOtFile(test_base.TestTranslationStore):
    StoreClass = ot.OmegaTFile
