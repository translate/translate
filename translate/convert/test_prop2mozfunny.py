from io import BytesIO

from translate.convert import prop2mozfunny


class TestPO2Prop(object):

    def merge2inc(self, incsource, posource):
        """helper that merges po translations to .inc source without requiring files"""
        inputfile = BytesIO(posource.encode('utf-8') if posource else None)
        templatefile = BytesIO(incsource.encode('utf-8'))
        outputfile = BytesIO()
        result = prop2mozfunny.po2inc(inputfile, outputfile, templatefile)
        outputinc = outputfile.getvalue().decode('utf-8')
        print(outputinc)
        assert result
        return outputinc

    def test_no_endlines_added(self):
        """check that we don't add newlines at the end of file"""
        posource = '''# converted from #defines file\n#: MOZ_LANG_TITLE\nmsgid "English (US)"\nmsgstr "Deutsch (DE)"\n\n'''
        inctemplate = '''#define MOZ_LANG_TITLE Deutsch (DE)\n'''
        incexpected = inctemplate
        incfile = self.merge2inc(inctemplate, posource)
        print(incfile)
        assert incfile == incexpected

    def test_uncomment_contributors(self):
        """check that we handle uncommenting contributors properly"""
        posource = '''# converted from #defines file
#: MOZ_LANGPACK_CONTRIBUTORS
msgid "<em:contributor>Joe Solon</em:contributor>"
msgstr "<em:contributor>Mr Fury</em:contributor>"
'''
        inctemplate = '''# #define MOZ_LANGPACK_CONTRIBUTORS <em:contributor>Joe Solon</em:contributor>\n'''
        incexpected = '''#define MOZ_LANGPACK_CONTRIBUTORS <em:contributor>Mr Fury</em:contributor>\n'''
        incfile = self.merge2inc(inctemplate, posource)
        print(incfile)
        assert incfile == incexpected

    def test_multiline_comment_newlines(self):
        """Ensure that we preserve newlines in multiline comments"""
        inctemplate = '''# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#filter emptyLines
'''
        incexpected = inctemplate
        incfile = self.merge2inc(inctemplate, None)
        print(incfile)
        assert incfile == incexpected
