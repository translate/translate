import os
import sys
import tempfile
from io import BytesIO

from translate.storage import po
from translate.tools import poconflicts
from translate.tools.poconflicts import ConflictOptionParser


def make_parser():
    """Create a ConflictOptionParser with the same options as main()."""
    formats = {"po": ("po", None), None: ("po", None)}
    parser = ConflictOptionParser(formats)
    parser.add_option(
        "-I",
        "--ignore-case",
        dest="ignorecase",
        action="store_true",
        default=False,
        help="ignore case distinctions",
    )
    parser.add_option(
        "-v",
        "--invert",
        dest="invert",
        action="store_true",
        default=False,
        help="invert the conflicts",
    )
    parser.add_option(
        "",
        "--accelerator",
        dest="accelchars",
        default="",
        metavar="ACCELERATORS",
        help="ignores accelerator characters when matching",
    )
    return parser


def make_po_bytes(units):
    """Create serialized PO bytes from a list of (source, target) tuples."""
    store = po.pofile()
    for source, target in units:
        unit = po.pounit(source)
        unit.target = target
        store.units.append(unit)
    buf = BytesIO()
    store.serialize(buf)
    return buf.getvalue()


def test_per_string_keeps_conflicts_with_the_same_filename_slug_separate(
    tmp_path, monkeypatch
):
    inputdir = tmp_path / "input"
    outputdir = tmp_path / "output"
    inputdir.mkdir()
    outputdir.mkdir()
    (inputdir / "a.po").write_bytes(
        make_po_bytes([("Co-operate", "Collaborer"), ("co operate", "Coopérer")])
    )
    (inputdir / "b.po").write_bytes(
        make_po_bytes([("co-operate", "S'entraider"), ("CO OPERATE", "Travailler")])
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "poconflicts",
            "--per-string",
            "-I",
            "-i",
            str(inputdir),
            "-o",
            str(outputdir),
        ],
    )

    poconflicts.main()

    reports = sorted(outputdir.glob("*.po"))
    assert [report.name for report in reports] == [
        "0001-co-operate.po",
        "0002-co-operate.po",
    ]
    groups = []
    for report in reports:
        with report.open("rb") as stream:
            groups.append(
                {unit.source.lower() for unit in po.pofile(stream).units if unit.source}
            )
    assert groups == [{"co operate"}, {"co-operate"}]


class TestConflictOptionParser:
    def run_conflicts(self, po_files_content, ignorecase=True):
        """Run conflict detection on multiple in-memory PO files and return output files."""
        parser = make_parser()
        with (
            tempfile.TemporaryDirectory() as inputdir,
            tempfile.TemporaryDirectory() as outputdir,
        ):
            for i, content in enumerate(po_files_content):
                with open(os.path.join(inputdir, f"file{i}.po"), "wb") as fh:
                    fh.write(content)

            options_args = ["-i", inputdir, "-o", outputdir]
            if ignorecase:
                options_args.append("-I")
            options, _ = parser.parse_args(options_args)
            parser.recursiveprocess(options)

            result = {}
            for fname in os.listdir(outputdir):
                fpath = os.path.join(outputdir, fname)
                with open(fpath, "rb") as fh:
                    result[fname] = fh.read()
            return result

    def test_games_gamess_no_keyerror(self):
        """
        Test that poconflicts does not raise KeyError when 'game', 'games', and 'gamess'
        all appear as conflict keys simultaneously (plural chain: game->games->gamess).
        """
        # "GAMESS input" vs "GAMESS Input" -> same lowercased source, two different translations
        file1 = make_po_bytes([("GAMESS input", "Données d'entrée GAMESS")])
        file2 = make_po_bytes([("GAMESS Input", "Entrée GAMESS")])
        # "New Game" -> two different translations
        file3 = make_po_bytes([("New Game", "Nouvelle partie")])
        file4 = make_po_bytes([("New Game", "Nouveau jeu")])
        # "Games" -> two different translations
        file5 = make_po_bytes([("Games", "Jeux")])
        file6 = make_po_bytes([("Games", "Jeux vidéo")])

        # Should not raise KeyError
        result = self.run_conflicts([file1, file2, file3, file4, file5, file6])
        assert len(result) > 0
