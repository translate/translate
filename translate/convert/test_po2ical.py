#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.convert import po2ical
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po

class TestPO2Ical:
    def po2ical(self, posource):
        """helper that converts po source to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2ical.reical()
        outputprop = convertor.convertstore(inputpo)
        return outputprop

    def merge2ical(self, propsource, posource):
        """helper that merges po translations to .properties source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(propsource)
        #templateprop = properties.propfile(templatefile)
        convertor = po2ical.reical(templatefile, inputpo)
        outputprop = convertor.convertstore()
        print outputprop
        return outputprop

class TestPO2IcalCommand(test_convert.TestConvertCommand, TestPO2Ical):
    """Tests running actual po2ical commands on files"""
    convertmodule = po2ical
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)

