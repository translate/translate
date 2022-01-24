from io import BytesIO

from translate.convert import mozfunny2prop
from translate.storage import po


class TestInc2PO:
    @staticmethod
    def inc2po(incsource, inctemplate=None):
        """helper that converts .inc source to po source without requiring files"""
        inputfile = BytesIO(incsource.encode())
        if inctemplate:
            templatefile = BytesIO(inctemplate.encode())
        else:
            templatefile = None
        outputfile = BytesIO()
        result = mozfunny2prop.inc2po(inputfile, outputfile, templatefile)
        assert result == 1
        outputpo = outputfile.getvalue()
        outputpofile = po.pofile(BytesIO(outputpo))
        return outputpofile

    @staticmethod
    def singleelement(pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        print(pofile)
        return pofile.units[1]

    @staticmethod
    def countelements(pofile):
        """counts the number of non-header entries"""
        assert pofile.units[0].isheader()
        print(pofile)
        return len(pofile.units) - 1

    def test_simpleentry(self):
        """checks that a simple inc entry converts properly to a po entry"""
        incsource = "#define MOZ_LANGPACK_CREATOR mozilla.org\n"
        pofile = self.inc2po(incsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["MOZ_LANGPACK_CREATOR"]
        assert pounit.source == "mozilla.org"
        assert pounit.target == ""

    def test_uncomment_contributors(self):
        """checks that the contributors entry is automatically uncommented"""
        incsource = """# If non-English locales wish to credit multiple contributors, uncomment this
# variable definition and use the format specified.
# #define MOZ_LANGPACK_CONTRIBUTORS <em:contributor>Joe Solon</em:contributor> <em:contributor>Suzy Solon</em:contributor>"""
        pofile = self.inc2po(incsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["MOZ_LANGPACK_CONTRIBUTORS"]
        assert "Joe Solon" in pounit.source
