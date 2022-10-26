import os

from translate.convert import po2idml, test_convert


class TestPo2IDMLCommand(test_convert.TestConvertCommand):
    """Tests running actual po2idml commands on files"""

    convertmodule = po2idml
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
    ]

    def test_convert(self):
        posource = """
#: idPkg:Story[0]/%7B%7DStory[0]/%7B%7DXMLElement[0]/%7B%7DParagraphStyleRange[0]
#: Stories/Story_mainmainmainmainmainmainmainmainmainmainmainu188.xml
msgid "<g id=\"0\"><g id=\"1\">THE HEADLINE HERE</g></g>"
msgstr "<g id=\"0\"><g id=\"1\">TADY JE NADPIS</g></g>"
"""
        self.create_testfile("simple.po", posource)
        self.run_command(
            i="simple.po",
            o="simple.idml",
            template=os.path.join(os.path.dirname(__file__), "test.idml"),
        )
