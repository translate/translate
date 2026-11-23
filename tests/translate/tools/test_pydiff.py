import sys
from pathlib import Path

import pytest

from translate.tools import pydiff


def test_directory_diff_sorts_and_deduplicates_filenames(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fromdir = tmp_path / "from"
    todir = tmp_path / "to"
    fromdir.mkdir()
    todir.mkdir()
    (fromdir / "zeta.txt").write_text("shared\n", encoding="utf-8")
    (fromdir / "alpha.txt").write_text("source only\n", encoding="utf-8")
    (todir / "zeta.txt").write_text("shared\n", encoding="utf-8")
    (todir / "middle.txt").write_text("target only\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["pydiff", "-s", str(fromdir), str(todir)])

    pydiff.main()

    assert capsys.readouterr().out.splitlines() == [
        f"Only in {fromdir}: alpha.txt",
        f"Only in {todir}: middle.txt",
        f"Files {fromdir / 'zeta.txt'} and {todir / 'zeta.txt'} are identical",
    ]
