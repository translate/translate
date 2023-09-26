from io import BytesIO

from translate.storage import test_base, tmx


class TestTMXUnit(test_base.TestTranslationUnit):
    UnitClass = tmx.tmxunit


class TestTMXUnitFromParsedString(TestTMXUnit):
    tmxsource = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx
  SYSTEM 'tmx14.dtd'>
<tmx version="1.4">
        <header adminlang="en" creationtool="Translate Toolkit" creationtoolversion="1.0beta" datatype="PlainText" o-tmf="UTF-8" segtype="sentence" srclang="en"/>
        <body>
                <tu>
                        <tuv xml:lang="en">
                                <seg>Test String</seg>
                        </tuv>
                </tu>
        </body>
</tmx>"""

    def setup_method(self, method):
        store = tmx.tmxfile.parsestring(self.tmxsource)
        self.unit = store.units[0]


class TestTMXfile(test_base.TestTranslationStore):
    StoreClass = tmx.tmxfile

    @staticmethod
    def tmxparse(tmxsource):
        """helper that parses tmx source without requiring files"""
        dummyfile = BytesIO(tmxsource)
        print(tmxsource)
        tmxfile = tmx.tmxfile(dummyfile)
        return tmxfile

    def test_translate(self):
        tmxfile = tmx.tmxfile()
        assert tmxfile.translate("Anything") is None
        tmxfile.addtranslation(
            "A string of characters", "en", "'n String karakters", "af"
        )
        assert tmxfile.translate("A string of characters") == "'n String karakters"

    def test_addtranslation(self):
        """tests that addtranslation() stores strings correctly"""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation(
            "A string of characters", "en", "'n String karakters", "af"
        )
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.translate("A string of characters") == "'n String karakters"

    def test_withcomment(self):
        """tests that addtranslation() stores string's comments correctly"""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation(
            "A string of chars", "en", "'n String karakters", "af", "comment"
        )
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.findunit("A string of chars").getnotes() == "comment"

    def test_withnewlines(self):
        """test addtranslation() with newlines"""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation(
            "First line\nSecond line", "en", "Eerste lyn\nTweede lyn", "af"
        )
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.translate("First line\nSecond line") == "Eerste lyn\nTweede lyn"

    @staticmethod
    def test_xmlentities():
        """Test that the xml entities '&' and '<'  are escaped correctly"""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation("Mail & News", "en", "Nuus & pos", "af")
        tmxfile.addtranslation("Five < ten", "en", "Vyf < tien", "af")
        xmltext = bytes(tmxfile).decode("utf-8")
        print("The generated xml:")
        print(xmltext)
        assert tmxfile.translate("Mail & News") == "Nuus & pos"
        assert xmltext.index("Mail &amp; News")
        assert xmltext.find("Mail & News") == -1
        assert tmxfile.translate("Five < ten") == "Vyf < tien"
        assert xmltext.index("Five &lt; ten")
        assert xmltext.find("Five < ten") == -1

    def test_controls_cleaning(self):
        """test addtranslation() with control chars"""
        tmxfile = tmx.tmxfile()
        tmxfile.addtranslation("Client Version:\x0314 %s", "en", "test one", "ar")
        tmxfile.addtranslation("Client Version:\n%s", "en", "test two", "ar")
        newfile = self.tmxparse(bytes(tmxfile))
        print(bytes(tmxfile))
        assert newfile.translate("Client Version:14 %s") == "test one"
        assert newfile.translate("Client Version:\n%s") == "test two"
