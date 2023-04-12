import subprocess
import sys

import pytest

from syrupy.assertion import SnapshotAssertion


pytestmark = [
    pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires python 3.8")
]

po_files = """
tests/cli/data/test_pocount_po_csv/one.po
tests/cli/data/test_pocount_po_file/one.po
tests/cli/data/test_pocount_po_fuzzy/one.po
""".split()


@pytest.mark.parametrize("format", ["csv", "full", "short-strings", "short-words"])
@pytest.mark.parametrize("incomplete", [True, False], ids=lambda v: f"incomplete={v}")
@pytest.mark.parametrize("no_color", [True, False], ids=lambda v: f"no-color={v}")
def test_pocount(format, incomplete, no_color, snapshot: SnapshotAssertion):
    opts = [f"--{format}"]
    if incomplete:
        opts.append("--incomplete")
    if no_color:
        opts.append("--no-color")

    stdout = subprocess.check_output(["pocount", *opts, *po_files], text=True)

    assert stdout == snapshot


@pytest.mark.parametrize("command", ["pocount"])
def test_help(command: str, snapshot: SnapshotAssertion):
    stdout = subprocess.check_output([command, "--help"], text=True)

    assert stdout == snapshot
