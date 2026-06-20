import logging
from pathlib import Path

from translate.storage import factory
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
