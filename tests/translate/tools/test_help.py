import subprocess
import sys
from pathlib import Path

import pytest

location = Path(__file__).parent.parent.parent.parent / "translate" / "tools"


@pytest.mark.parametrize(
    "command",
    [
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
def test_help(command: str) -> None:
    stdout = subprocess.check_output(
        [sys.executable, str(location / f"{command}.py"), "--help"],
        text=True,
    )

    assert stdout
    assert command in stdout
    assert "--help" in stdout
