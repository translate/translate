import pytest

from translate.storage import subtitles, test_monolingual


class TestSubtitleUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = subtitles.SubtitleUnit

    @pytest.mark.xfail(reason="Not Implemented")
    def test_note_sanity(self):
        super().test_note_sanity()


class TestSubRipFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.SubRipFile


@pytest.mark.xfail(reason="Broken, #4155")
class TestMicroDVDFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.MicroDVDFile


@pytest.mark.xfail(reason="Broken, #4155")
class TestAdvSubStationAlphaFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.AdvSubStationAlphaFile


@pytest.mark.xfail(reason="Broken, #4155")
class TestSubStationAlphaFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.SubStationAlphaFile
