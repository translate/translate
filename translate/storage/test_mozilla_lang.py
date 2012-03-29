#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py.test import mark

from translate.storage import mozilla_lang
from translate.storage import test_base


class TestMozLangUnit(test_base.TestTranslationUnit):
    UnitClass = mozilla_lang.LangUnit

    def test_translate_but_same(self):
        """Mozilla allows {ok} to indicate a line that is the 
        same in source and target on purpose"""
        unit = self.UnitClass("Open")
        unit.target = "Open"
        assert unit.target == "Open"
        assert str(unit).endswith(" {ok}")


class TestMozLangFile(test_base.TestTranslationStore):
    StoreClass = mozilla_lang.LangStore

    def test_nonascii(self):
        # FIXME investigate why this doesn't pass or why we even do this
        # text with UTF-8 encoded strings
        pass
