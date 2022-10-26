import os

from translate.convert import test_convert, xliff2odf


class TestXLIFF2ODFommand(test_convert.TestConvertCommand):
    """Tests running actual xliff2odf commands on files"""

    convertmodule = xliff2odf
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
    ]

    def test_convert(self):
        xliffsource = """<?xml version="1.0" ?>
    <xliff version="1.1">
      <file original="filename.po" source-language="en-US" datatype="po">
        <body>
         <trans-unit xml:space="preserve" id="1" approved="yes">
           <source>Hello, world!</source>
           <target state="translated">Ahoj světe!</target>
         </trans-unit>
        </body>
      </file>
    </xliff>"""
        self.create_testfile("simple.xlf", xliffsource)
        self.run_command(
            i="simple.xlf",
            o="simple.odt",
            template=os.path.join(os.path.dirname(__file__), "test.odt"),
        )
