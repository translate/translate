#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import test_base
from translate.storage import omegat as ot


class TestOtUnit(test_base.TestTranslationUnit):
    UnitClass = ot.OmegaTUnit

    def test_note_sanity(self):
        # We don't have notes in an OmegaT terminology file
        pass


class TestOtFile(test_base.TestTranslationStore):
    StoreClass = ot.OmegaTFile
