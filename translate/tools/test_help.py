import subprocess
import sys
from pathlib import Path

import pytest


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
def test_help(command: str):
    stdout = subprocess.check_output(
        [sys.executable, str(Path(__file__).parent / f"{command}.py"), "--help"],
        text=True,
    )

    assert stdout
    assert command in stdout
    assert "--help" in stdout
