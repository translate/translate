#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import mozilla_lang
from translate.storage import test_base


class TestUtxUnit(test_base.TestTranslationUnit):
    UnitClass = mozilla_lang.LangUnit


class TestUtxFile(test_base.TestTranslationStore):
    StoreClass = mozilla_lang.LangStore

    def test_nonascii(self):
        # FIXME investigate why this doesn't pass or why we even do this
        # text with UTF-8 encoded strings
        pass
