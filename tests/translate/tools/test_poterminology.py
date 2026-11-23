import logging
from pathlib import Path

from translate.storage import factory, po
from translate.tools import poterminology

base_dir = Path(__file__).parent.parent.parent
sample_po_file = base_dir / "xliff_conformance" / "af-pootle.po"


class TestPOTerminology:
    def test_term_extraction(self) -> None:
        """Test basic term extraction/filtering from a po file."""
        extractor = poterminology.TerminologyExtractor()
        # When no content has been provided, returns a simple dict
        assert extractor.extract_terms() == {}

        with open(sample_po_file, "rb") as fh:
            inputfile = factory.getobject(fh)
        extractor.processunits(inputfile.units, str(sample_po_file))
        terms = extractor.extract_terms()
        assert len(terms) > 50
        assert "default" in terms

        filtered_terms = extractor.filter_terms(terms)
        assert filtered_terms[0][0] > filtered_terms[-1][0]

    def test_unitinfo_stores_minimal_data(self) -> None:
        """Test that UnitInfo stores minimal data instead of full unit objects."""
        extractor = poterminology.TerminologyExtractor()

        with open(sample_po_file, "rb") as fh:
            inputfile = factory.getobject(fh)

        # Process units
        extractor.processunits(inputfile.units, str(sample_po_file))

        # Check that glossary contains UnitInfo objects, not full unit objects
        for translations in extractor.glossary.values():
            for _source, _target, unit_info, _filename in translations:
                # Verify it's a UnitInfo namedtuple
                assert isinstance(unit_info, poterminology.UnitInfo)
                # Verify it has the expected attributes
                assert hasattr(unit_info, "source")
                assert hasattr(unit_info, "target")
                assert hasattr(unit_info, "locations")
                assert hasattr(unit_info, "sourcenotes")
                assert hasattr(unit_info, "transnotes")
                # Verify locations and notes are frozensets (immutable, memory-efficient)
                assert isinstance(unit_info.locations, frozenset)
                assert isinstance(unit_info.sourcenotes, frozenset)
                assert isinstance(unit_info.transnotes, frozenset)
                break
            break

    def test_bad_stopword_entry_keeps_previous_entries_and_stops(
        self, tmp_path, caplog
    ) -> None:
        """Invalid stopword actions should not discard already parsed entries."""
        stopfile = tmp_path / "stopwords"
        stopfile.write_text("+keep\n?bad\n=ignored\n")

        with caplog.at_level(logging.WARNING):
            extractor = poterminology.TerminologyExtractor(stopfile=str(stopfile))

        assert extractor.stopwords["keep"] == frozenset()
        assert "ignored" not in extractor.stopwords
        assert "bad stopword entry starts with" in caplog.text
        assert "all lines after error ignored" in caplog.text

    def test_multiple_translations_sorted_by_frequency(self) -> None:
        """Multiple translations for a term should be ordered by frequency."""
        file_translations = [
            ("a.po", "parti"),
            ("b.po", "spel"),
            ("c.po", "spel"),
            ("d.po", "spel"),
        ]
        extractor = poterminology.TerminologyExtractor()
        for filename, target in file_translations:
            unit = po.pounit("game")
            unit.target = target
            extractor.processunits([unit], filename)

        terms = extractor.extract_terms(inputmin=1, fullmsgmin=1, locmin=1)
        termunit = terms["game"][1]
        assert termunit.target == "spel {b.po, c.po, d.po}; parti {a.po}"
        assert termunit.isfuzzy()

    def test_equal_frequency_translations_preserve_encounter_order(self) -> None:
        """Targets with equal occurrence counts should stay in encounter order."""
        termunit = poterminology.create_termunit(
            term="example",
            unit=None,
            targets={
                "alpha": ["a.po", "b.po"],
                "beta": ["c.po", "d.po"],
                "gamma": ["e.po", "f.po", "g.po"],
            },
            locations=set(),
            sourcenotes=set(),
            transnotes=set(),
            filecounts={},
        )
        assert (
            termunit.target
            == "gamma {e.po, f.po, g.po}; alpha {a.po, b.po}; beta {c.po, d.po}"
        )

    def test_create_termunit_update_note_sorted_by_frequency(self) -> None:
        """Translator notes for existing multi-term units should also sort by frequency."""
        existing = po.pounit("game")
        existing.target = "old {x.po}; older {y.po}"

        termunit = poterminology.create_termunit(
            term="game",
            unit=existing,
            targets={
                "parti": ["a.po"],
                "spel": ["b.po", "c.po", "d.po"],
            },
            locations=set(),
            sourcenotes=set(),
            transnotes=set(),
            filecounts={},
        )
        assert termunit.target == "old {x.po}; older {y.po}"
        assert "spel {b.po, c.po, d.po}; parti {a.po}" in termunit.getnotes(
            "translator"
        )
