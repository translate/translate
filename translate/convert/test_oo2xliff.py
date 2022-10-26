import os

from translate.convert import oo2xliff, test_convert, test_oo2po
from translate.storage import oo, xliff


class TestOO2XLIFF(test_oo2po.TestOO2PO):
    target_filetype = xliff.xlifffile
    conversion_module = oo2xliff
    conversion_class = oo2xliff.oo2xliff

    def test_msgid_bug_error_address(self):
        pass


class TestOO2POCommand(test_convert.TestConvertCommand, TestOO2XLIFF):
    """Tests running actual oo2xliff commands on files"""

    convertmodule = oo2xliff

    expected_options = [
        "--source-language=LANG",
        "-l LANG, --language=LANG",
        "--duplicates=DUPLICATESTYLE",
        "--multifile=MULTIFILESTYLE",
        "--nonrecursiveinput",
    ]

    def test_preserve_filename(self):
        """Ensures that the filename is preserved."""
        oosource = rb"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58"
        self.create_testfile("snippet.sdf", oosource)
        oofile = oo.oofile(self.open_testfile("snippet.sdf"))
        assert oofile.filename.endswith("snippet.sdf")
        oofile.parse(oosource)
        assert oofile.filename.endswith("snippet.sdf")

    def test_simple_xlf(self):
        """tests the simplest possible conversion to a xlf file"""
        oosource = r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58"
        self.create_testfile("simple.oo", oosource)
        self.run_command("simple.oo", "simple.xlf", lang="ku", nonrecursiveinput=True)
        pofile = self.target_filetype(self.open_testfile("simple.xlf"))
        poelement = self.singleelement(pofile)
        assert poelement.source == "Character"
        assert poelement.target == ""

    def test_simple_po(self):
        """tests the simplest possible conversion to a po file"""
        oosource1 = r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58"
        oosource2 = r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	ku	Karakter				20050924 09:13:58"
        self.create_testfile("simple.oo", oosource1 + "\n" + oosource2)
        self.run_command("simple.oo", "simple.po", lang="ku", nonrecursiveinput=True)
        pofile = self.target_filetype(self.open_testfile("simple.po"))
        poelement = self.singleelement(pofile)
        assert poelement.source == "Character"
        assert poelement.target == "Karakter"

    def test_onefile_nonrecursive(self):
        """tests the --multifile=onefile option and make sure it doesn't produce a directory"""
        oosource = r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58"
        self.create_testfile("simple.oo", oosource)
        self.run_command("simple.oo", "simple.xlf", lang="ku", multifile="onefile")
        assert os.path.isfile(self.get_testfilename("simple.xlf"))
