#
# These test classes should be used as super class of test classes for the
# classes that doesn't support the target property

from translate.storage import base, test_base


class TestMonolingualUnit(test_base.TestTranslationUnit):
    UnitClass = base.TranslationUnit

    def test_target(self):
        pass

    def test_rich_get(self):
        pass

    def test_rich_set(self):
        pass


class TestMonolingualStore(test_base.TestTranslationStore):
    StoreClass = base.TranslationStore

    def test_translate(self):
        pass

    def test_markup(self):
        pass

    def test_nonascii(self):
        pass

    def check_equality(self, store1, store2):
        """Check that store1 and store2 are the same."""
        assert len(store1.units) == len(store2.units)

        for n, store1unit in enumerate(store1.units):
            store2unit = store2.units[n]

            print("match failed between elements %d of %d" % (n + 1, len(store1.units)))
            print("store1:")
            print(bytes(store1))
            print("store2:")
            print(bytes(store2))
            print("store1.units[%d].__dict__:" % n, store1unit.__dict__)
            print("store2.units[%d].__dict__:" % n, store2unit.__dict__)
            assert str(store1unit) == str(store2unit)
