# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pytest import importorskip

from translate.convert import ini2po
from translate.misc import wStringIO


importorskip("iniparse")


class TestIni2PO(object):

    def test_convert_empty_file(self):
        """Check converting empty INI returns no output."""
        input_file = wStringIO.StringIO('')
        output_file = wStringIO.StringIO()
        template_file = None
        result = ini2po.run_converter(input_file, output_file, template_file)
        assert result == 0
        assert output_file.getvalue() == ''
