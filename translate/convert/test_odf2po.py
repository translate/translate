#!/usr/bin/env python

from translate.convert import sxw2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po

class TestSxw2PO:
  pass

class TestSxw2POCommand(test_convert.TestConvertCommand, TestSxw2PO):
    """Tests running actual sxw2po commands on files"""
    convertmodule = sxw2po

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "", last=True)
