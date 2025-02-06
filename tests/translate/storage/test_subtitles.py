import pytest

from translate.storage import subtitles

from . import test_monolingual


class TestSubRipFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.SubRipFile

    def test_ordering(self):
        store = self.StoreClass()
        unit = store.UnitClass("Second")
        unit.settime("00:01:00.000", "00:01:01.000", 1)
        store.addunit(unit)
        unit = store.UnitClass("First")
        unit.settime("00:00:00.000", "00:00:01.000", 1)
        store.addunit(unit)
        content = bytes(store)

        newstore = self.StoreClass()
        newstore.parse(content)
        assert len(newstore.units) == 2
        assert newstore.units[0].source == "First"
        assert newstore.units[1].source == "Second"


class TestSubtitleUnit(TestSubRipFile):
    UnitClass = subtitles.SubtitleUnit

    @pytest.mark.xfail(reason="Not Implemented")
    def test_note_sanity(self):
        super().test_note_sanity()


class TestMicroDVDFile(TestSubRipFile):
    StoreClass = subtitles.MicroDVDFile


class TestAdvSubStationAlphaFile(TestSubRipFile):
    StoreClass = subtitles.AdvSubStationAlphaFile


class TestSubStationAlphaFile(TestSubRipFile):
    StoreClass = subtitles.SubStationAlphaFile
