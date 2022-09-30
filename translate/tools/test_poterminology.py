import os

from translate.storage import factory
from translate.tools import poterminology


base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sample_po_file = os.path.join(base_dir, "tests", "xliff_conformance", "af-pootle.po")


class TestPOTerminology:
    @staticmethod
    def test_term_extraction():
        """Test basic term extraction/filtering from a po file."""
        extractor = poterminology.TerminologyExtractor()
        # When no content has been provided, returns a simple dict
        assert extractor.extract_terms() == {}

        with open(sample_po_file, "rb") as fh:
            inputfile = factory.getobject(fh)
        extractor.processunits(inputfile.units, sample_po_file)
        terms = extractor.extract_terms()
        assert len(terms) > 50
        assert "default" in terms

        filtered_terms = extractor.filter_terms(terms)
        assert filtered_terms[0][0] > filtered_terms[-1][0]
