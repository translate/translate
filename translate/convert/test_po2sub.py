from io import BytesIO

from pytest import importorskip

from translate.convert import po2sub, test_convert
from translate.storage import po


# Technically subtitles can also use an older gaupol
importorskip("aeidon")


class TestPO2Sub:
    @staticmethod
    def po2sub(posource):
        """helper that converts po source to subtitle source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        convertor = po2sub.po2sub()
        outputsub = convertor.convert_store(inputpo)
        return outputsub.decode("utf-8")

    @staticmethod
    def merge2sub(subsource, posource):
        """helper that merges po translations to subtitle source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        templatefile = BytesIO(subsource.encode())
        convertor = po2sub.po2sub(templatefile, inputpo)
        outputsub = convertor.convert_store()
        print(outputsub)
        return outputsub.decode("utf-8")

    def test_subrip(self):
        """test SubRip or .srt files."""
        posource = """#: 00:00:20.000-->00:00:24.400
msgid "Altocumulus clouds occur between six thousand"
msgstr "Blah blah blah blah"

#: 00:00:24.600-->00:00:27.800
msgid "and twenty thousand feet above ground level."
msgstr "Koei koei koei koei"
"""
        subtemplate = """1
00:00:20,000 --> 00:00:24,400
Altocumulus clouds occur between six thousand

2
00:00:24,600 --> 00:00:27,800
and twenty thousand feet above ground level.
"""
        subexpected = """1
00:00:20,000 --> 00:00:24,400
Blah blah blah blah

2
00:00:24,600 --> 00:00:27,800
Koei koei koei koei
"""
        subfile = self.merge2sub(subtemplate, posource)
        print(subexpected)
        assert subfile == subexpected


class TestPO2SubCommand(test_convert.TestConvertCommand, TestPO2Sub):
    """Tests running actual po2sub commands on files"""

    convertmodule = po2sub
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]
