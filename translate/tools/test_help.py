import subprocess

import pytest

from ._test_utils import requires_py38_mark


@requires_py38_mark
@pytest.mark.parametrize(
    "command",
    [
        "build_tmdb",
        "phppo2pypo",
        "poclean",
        "pocompile",
        "poconflicts",
        "pocount",
        "podebug",
        "pogrep",
        "pomerge",
        "porestructure",
        "posegment",
        "poswap",
        "poterminology",
        "pretranslate",
        "pydiff",
        "pypo2phppo",
    ],
)
def test_help(command: str, snapshot):
    stdout = subprocess.check_output([command, "--help"], text=True)

    assert stdout == snapshot
