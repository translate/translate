from io import BytesIO

from translate.convert import android2po

from . import test_convert


class TestAndroid2PO:
    @staticmethod
    def android2po(source, template=None):
        """helper that converts android source to po source without requiring files"""
        inputfile = BytesIO(source.encode())
        templatefile = BytesIO(template.encode()) if template else None
        outputpo = android2po._convertandroid(inputfile, templatefile)
        return outputpo

    def test_no_template_units(self):
        """test that we can handle android with no template"""

        _input = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Multimedia tab</string>
</resources>"""

        poresult = self.android2po(_input)
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "Multimedia tab"

    def test_template_units(self):
        """test that we can handle android with template"""

        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Multimedia tab</string>
</resources>"""
        _input = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Pestanya multimèdia</string>
</resources>"""

        poresult = self.android2po(_input, template)
        assert len(poresult.units) == 2
        assert poresult.units[1].source == "Multimedia tab"
        assert poresult.units[1].target == "Pestanya multimèdia"


class TestAndroid2POCommand(test_convert.TestConvertCommand, TestAndroid2PO):
    """Tests running actual android2po commands on files"""

    convertmodule = android2po

    expected_options = [
        "--duplicates",
        "-t TEMPLATE, --template=TEMPLATE",
    ]

    def test_convertandroid(self):
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
<string name="id">Multimedia tab</string>
</resources>"""

        strings_file = "strings.xml"
        po_file = "en.po"
        self.create_testfile(strings_file, content)

        self.run_command(strings_file, po_file)
        content = self.open_testfile(po_file, "r").read().split("\n\n")[1]
        assert """msgid "Multimedia tab""" in content
