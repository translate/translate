from io import BytesIO

from translate.convert import ts2po

from . import test_convert


class TestTS2PO:
    @staticmethod
    def ts2po(tssource):
        converter = ts2po.ts2po()
        tsfile = BytesIO(tssource.encode())
        outputpo = converter.convertfile(tsfile)
        print("The generated po:")
        print(bytes(outputpo))
        return outputpo

    def test_blank(self):
        """tests blank conversion"""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>MainWindowBase</name>
    <message>
        <source>Project:</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert len(pofile.units) == 2
        assert pofile.units[1].source == "Project:"
        assert pofile.units[1].target == ""
        assert pofile.units[1].getlocations()[0].startswith("MainWindowBase")
        assert not pofile.units[1].isfuzzy()

    def test_basic(self):
        """tests basic conversion"""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>AboutDialog</name>
    <message>
        <source>&amp;About</source>
        <translation>&amp;Giới thiệu</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert len(pofile.units) == 2
        assert pofile.units[1].source == "&About"
        assert pofile.units[1].target == "&Giới thiệu"
        assert pofile.units[1].getlocations()[0].startswith("AboutDialog")

    def test_unfinished(self):
        """tests unfinished conversion"""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>MainWindowBase</name>
    <message>
        <source>Project:</source>
        <translation type="unfinished">Projek vergardering</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert len(pofile.units) == 2
        assert pofile.units[1].source == "Project:"
        assert pofile.units[1].target == "Projek vergardering"
        assert pofile.units[1].getlocations()[0].startswith("MainWindowBase")
        assert pofile.units[1].isfuzzy()

    def test_multiline(self):
        """tests multiline message conversion"""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>@default</name>
    <message>
        <source>Source with
new line</source>
        <translation>Test with
new line</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert len(pofile.units) == 2
        assert pofile.units[1].source == "Source with\nnew line"
        assert pofile.units[1].target == "Test with\nnew line"
        assert pofile.units[1].getlocations()[0].startswith("@default")

    def test_obsolete(self):
        """test the handling of obsolete TS entries"""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>Obsoleted</name>
    <message>
        <source>Failed</source>
        <translation type="obsolete">Mislukt</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert pofile.units[1].getnotes("developer") == "(obsolete)"
        # Test that we aren't following the old style
        assert "_ OBSOLETE" not in pofile.units[1].getnotes()

    def test_comment(self):
        """test that we can handle disambiguation identifiers."""
        # Example from https://www.gnu.org/software/gettext/manual/html_node/Contexts.html
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>FileMenu</name>
    <message>
        <source>&amp;Open</source>
        <comment>Menu|File|</comment>
        <translation>&amp;Abrir</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert pofile.units[1].getcontext() == "Menu|File|"

    def test_extracomment(self):
        """test that we can handle '//:' comments from developers to translators."""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name>AboutDialog</name>
    <message>
        <source>&amp;About</source>
        <extracomment>Appears in the Help menu (on Windows and Linux) or the app menu (on macOS).</extracomment>
        <translation>&amp;Giới thiệu</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert (
            pofile.units[1].getnotes()
            == "Appears in the Help menu (on Windows and Linux) or the app menu (on macOS)."
        )

    def test_emptycontext(self):
        """test conversion with a leading empty context"""
        tssource = """<!DOCTYPE TS><TS>
<context>
    <name></name>
    <message>
        <source>Message to ignore</source>
        <translation>Missatge a ignorar</translation>
    </message>
</context>
<context>
    <name>ValidContext</name>
    <message>
        <source>Since we come from abroad, we thought the best thing we could do was to learn the local language and integrate ourselves.</source>
        <translation>Com que venim de fora vam pensar que el millor que podíem fer era aprendre la llengua d'aquí i integrar-nos.</translation>
    </message>
</context>
</TS>
"""
        pofile = self.ts2po(tssource)
        assert (
            pofile.units[1].source
            == "Since we come from abroad, we thought the best thing we could do was to learn the local language and integrate ourselves."
        )
        assert (
            pofile.units[1].target
            == "Com que venim de fora vam pensar que el millor que podíem fer era aprendre la llengua d'aquí i integrar-nos."
        )


class TestTS2POCommand(test_convert.TestConvertCommand, TestTS2PO):
    """Tests running actual ts2po commands on files"""

    convertmodule = ts2po
    expected_options = [
        "--duplicates=DUPLICATESTYLE",
        "-P, --pot",
    ]
