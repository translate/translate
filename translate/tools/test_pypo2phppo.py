# pypo2phppo unit tests
# Author: Wil Clouser <wclouser@mozilla.com>
# Date: 2009-12-03

from io import BytesIO

from translate.convert import test_convert
from translate.tools import pypo2phppo


class TestPyPo2PhpPo:
    @staticmethod
    def test_single_po():
        inputfile = b"""
# This user comment refers to: {0}
#. This developer comment does too: {0}
#: some/path.php:111
#, php-format
msgid "I have {1} apples and {0} oranges"
msgstr "I have {1} apples and {0} oranges"
        """
        outputfile = BytesIO()
        pypo2phppo.convertpy2php(inputfile, outputfile)

        output = outputfile.getvalue().decode("utf-8")

        assert "refers to: %1$s" in output
        assert "does too: %1$s" in output
        assert 'msgid "I have %2$s apples and %1$s oranges"' in output
        assert 'msgstr "I have %2$s apples and %1$s oranges"' in output

    @staticmethod
    def test_plural_po():
        inputfile = b"""
#. This developer comment refers to {0}
#: some/path.php:111
#, php-format
msgid "I have {0} apple"
msgid_plural "I have {0} apples"
msgstr[0] "I have {0} apple"
msgstr[1] "I have {0} apples"
        """
        outputfile = BytesIO()
        pypo2phppo.convertpy2php(inputfile, outputfile)
        output = outputfile.getvalue().decode("utf-8")

        assert 'msgid "I have %1$s apple"' in output
        assert 'msgid_plural "I have %1$s apples"' in output
        assert 'msgstr[0] "I have %1$s apple"' in output
        assert 'msgstr[1] "I have %1$s apples"' in output


class TestPyPo2PhpPoCommand(test_convert.TestConvertCommand, TestPyPo2PhpPo):
    """Tests running actual pypo2phppo commands on files"""

    convertmodule = pypo2phppo
    defaultoptions = {}
