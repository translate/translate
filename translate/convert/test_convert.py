import os
import re
from itertools import chain

import pytest

from translate.convert import convert


OPTION_RE = re.compile(r"^\s*-")


class TestConvertCommand:
    """Tests running actual commands on files"""

    convertmodule = convert
    defaultoptions = {"progress": "none"}
    expected_options = []

    def setup_method(self, method):
        """creates a clean test directory for the given method"""
        self.testdir = f"{self.__class__.__name__}_{method.__name__}"
        self.cleardir()
        os.mkdir(self.testdir)
        self.rundir = os.path.abspath(os.getcwd())

    def teardown_method(self, method):
        """removes the test directory for the given method"""
        os.chdir(self.rundir)
        self.cleardir()

    def cleardir(self):
        """removes the test directory"""
        if os.path.exists(self.testdir):
            for dirpath, subdirs, filenames in os.walk(self.testdir, topdown=False):
                for name in filenames:
                    os.remove(os.path.join(dirpath, name))
                for name in subdirs:
                    os.rmdir(os.path.join(dirpath, name))
        if os.path.exists(self.testdir):
            os.rmdir(self.testdir)
        assert not os.path.exists(self.testdir)

    def run_command(self, *argv, **kwargs):
        """runs the command via the main function, passing self.defaultoptions and keyword arguments as --long options and argv arguments straight"""
        os.chdir(self.testdir)
        argv = list(argv)
        kwoptions = getattr(self, "defaultoptions", {}).copy()
        kwoptions.update(kwargs)
        for key, value in kwoptions.items():
            if value is True:
                argv.append("--%s" % key)
            else:
                argv.append(f"--{key}={value}")
        try:
            self.convertmodule.main(argv)
        finally:
            os.chdir(self.rundir)

    def get_testfilename(self, filename):
        """gets the path to the test file"""
        return os.path.join(self.testdir, filename)

    def open_testfile(self, filename, mode="rb"):
        """opens the given filename in the testdirectory in the given mode"""
        filename = self.get_testfilename(filename)
        if not mode.startswith("r"):
            subdir = os.path.dirname(filename)
            currentpath = ""
            if not os.path.isdir(subdir):
                for part in subdir.split(os.sep):
                    currentpath = os.path.join(currentpath, part)
                    if not os.path.isdir(currentpath):
                        os.mkdir(currentpath)
        return open(filename, mode)

    def create_testfile(self, filename, contents):
        """creates the given file in the testdirectory with the given contents"""
        if isinstance(contents, str):
            contents = contents.encode("utf-8")
        testfile = self.open_testfile(filename, "wb")
        testfile.write(contents)
        testfile.close()

    def read_testfile(self, filename):
        """reads the given file in the testdirectory and returns the contents"""
        with open(self.get_testfilename(filename), "rb") as testfile:
            content = testfile.read()
        return content

    @staticmethod
    def help_check(options, option, last=False):
        """check that a help string occurs and remove it"""
        assert option in options
        newoptions = []
        for line in options.splitlines():
            if option in line or not line.lstrip().startswith("-"):
                continue
            newoptions.append(line)
        if last:
            assert newoptions == []
        return "\n".join(newoptions)

    def test_help(self, capsys):
        """tests getting help (returning the help_string so further tests can be done)"""
        with pytest.raises(SystemExit):
            self.run_command(help=True)
        help_string, err = capsys.readouterr()
        # normalize newlines
        help_lines = help_string.splitlines()
        print(help_lines)

        # summary documentation
        convertsummary = self.convertmodule.__doc__.split("\n")[0]
        # the convertsummary might be wrapped. this will probably unwrap it
        assert convertsummary in " ".join(help_lines)

        # usage line
        usageline = help_lines[0]
        assert usageline.startswith("Usage: ")
        assert "[--version] [-h|--help]" in usageline
        for line in help_lines:
            print(line)

        # extract options
        options = [
            line.lstrip()
            for line in help_lines[help_lines.index("Options:") + 1 :]
            if OPTION_RE.match(line)
        ]

        # Verify all expected options are present
        base_options = [
            "--progress=PROGRESS",
            "--version",
            "-h, --help",
            "--manpage",
            "--errorlevel=ERRORLEVEL",
            "-i INPUT, --input=INPUT",
            "-x EXCLUDE, --exclude=EXCLUDE",
            "-o OUTPUT, --output=OUTPUT",
            "-S, --timestamp",
        ]
        for expected in chain(base_options, self.expected_options):
            start = len(options)
            options = [option for option in options if not option.startswith(expected)]
            assert start - 1 == len(options), f"{expected} not found in {options}"

        # We should parse all the options
        assert options == []
