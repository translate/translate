from translate.search import terminology


class TestTerminology:
    """Test terminology matching"""

    @staticmethod
    def test_basic():
        """Tests basic functionality"""
        termmatcher = terminology.TerminologyComparer()
        assert termmatcher.similarity("Open the file", "file") > 75
