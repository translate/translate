from io import BytesIO

from translate.convert import android2po, test_convert
from translate.storage import aresource


class TestAndroid2PO:
    @staticmethod
    def android2po(source, template=None):
        """helper that converts android source to po source without requiring files"""
        inputfile = BytesIO(source.encode())
        inputandroid = aresource.AndroidResourceFile(inputfile)
        convertor = android2po.android2po()

        if template:
            templatefile = BytesIO(template.encode())
            templateandroid = aresource.AndroidResourceFile(templatefile)
            outputpo = convertor.merge_store(templateandroid, inputandroid)
        else:
            outputpo = convertor.convert_store(inputandroid)
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
