# phppo2pypo unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2009-12-03

from io import BytesIO

from translate.convert import test_convert
from translate.tools import phppo2pypo


class TestPhpPo2PyPo:
    @staticmethod
    def test_single_po():
        inputfile = b"""
# This user comment refers to: %1$s
#. This developer comment does too: %1$s
#: some/path.php:111
#, php-format
msgid "I have %2$s apples and %1$s oranges"
msgstr "I have %2$s apples and %1$s oranges"
        """
        outputfile = BytesIO()
        phppo2pypo.convertphp2py(inputfile, outputfile)

        output = outputfile.getvalue().decode("utf-8")

        assert "refers to: {0}" in output
        assert "does too: {0}" in output
        assert 'msgid "I have {1} apples and {0} oranges"' in output
        assert 'msgstr "I have {1} apples and {0} oranges"' in output

    @staticmethod
    def test_plural_po():
        inputfile = b"""
#. This developer comment refers to %1$s
#: some/path.php:111
#, php-format
msgid "I have %1$s apple"
msgid_plural "I have %1$s apples"
msgstr[0] "I have %1$s apple"
msgstr[1] "I have %1$s apples"
        """
        outputfile = BytesIO()
        phppo2pypo.convertphp2py(inputfile, outputfile)
        output = outputfile.getvalue().decode("utf-8")

        assert 'msgid "I have {0} apple"' in output
        assert 'msgid_plural "I have {0} apples"' in output
        assert 'msgstr[0] "I have {0} apple"' in output
        assert 'msgstr[1] "I have {0} apples"' in output


class TestPhpPo2PyPoCommand(test_convert.TestConvertCommand, TestPhpPo2PyPo):
    """Tests running actual phppo2pypo commands on files"""

    convertmodule = phppo2pypo
    defaultoptions = {}
