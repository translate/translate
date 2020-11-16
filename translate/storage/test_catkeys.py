from translate.storage import catkeys, test_base


class TestCatkeysUnit(test_base.TestTranslationUnit):
    UnitClass = catkeys.CatkeysUnit

    def test_difficult_escapes(self):
        r"""
        Catkeys files need to perform magic with escapes.

        Catkeys does not accept line breaks in its TM (even though they would
        be valid in CSV) thus we turn \\n into \n and reimplement the base
        class test but eliminate a few of the actual tests.
        """
        unit = self.unit
        specials = ['\\"', "\\ ", "\\\n", "\\\t", "\\\\r", '\\\\"']
        for special in specials:
            unit.source = special
            print("unit.source:", repr(unit.source) + "|")
            print("special:", repr(special) + "|")
            assert unit.source == special

    def test_newlines(self):
        """Wordfast does not like real newlines"""
        unit = self.UnitClass("One\nTwo")
        assert unit.dict["source"] == "One\\nTwo"

    def test_istranslated(self):
        unit = self.UnitClass()
        assert not unit.istranslated()
        unit.source = "Test"
        assert not unit.istranslated()
        unit.target = "Rest"
        assert unit.istranslated()

    def test_note_sanity(self):
        """Override test, since the format doesn't support notes."""
        pass


class TestCatkeysFile(test_base.TestTranslationStore):
    StoreClass = catkeys.CatkeysFile

    def test_checksum(self):
        """Tests that the checksum for a file is properly calculated."""
        # The following test is based on: https://github.com/haiku/haiku/blob/d30c60446a40ba4aa1418a548c82e6aaf72b409a/data/catalogs/add-ons/disk_systems/fat/tr.catkeys
        store = self.StoreClass()
        unit1 = store.addsourceunit("Auto (default)")
        unit1.setcontext("FAT_Initialize_Parameter")
        unit2 = store.addsourceunit("FAT bits:")
        unit2.setcontext("FAT_Initialize_Parameter")
        unit3 = store.addsourceunit("Name:")
        unit3.setcontext("FAT_Initialize_Parameter")
        assert store._compute_fingerprint() == 2766737426

        # setting translations should not change the fingerprint
        unit1.target = "Otomatik (öntanımlı)"
        unit2.target = "FAT bitleri:"
        unit3.target = "Ad:"
        assert store._compute_fingerprint() == 2766737426

        # changing a source string should change the fingerprint
        unit1.source = "Auto(no longer default)"
        assert store._compute_fingerprint() != 2766737426
