import pytest

from translate.storage import subtitles, test_monolingual


class TestSubtitleUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = subtitles.SubtitleUnit

    @pytest.mark.xfail(reason="Not Implemented")
    def test_note_sanity(self):
        super().test_note_sanity()


class TestSubRipFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.SubRipFile


class TestMicroDVDFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.MicroDVDFile


class TestAdvSubStationAlphaFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.AdvSubStationAlphaFile


class TestSubStationAlphaFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.SubStationAlphaFile
