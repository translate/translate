import pytest

from translate.storage import subtitles

from . import test_monolingual


class TestSubRipFile(test_monolingual.TestMonolingualStore):
    StoreClass = subtitles.SubRipFile

    def test_ordering(self) -> None:
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
    def test_note_sanity(self) -> None:
        super().test_note_sanity()  # ty:ignore[unresolved-attribute]


class TestMicroDVDFile(TestSubRipFile):
    StoreClass = subtitles.MicroDVDFile


class TestAdvSubStationAlphaFile(TestSubRipFile):
    StoreClass = subtitles.AdvSubStationAlphaFile

    def test_style_preservation(self) -> None:
        """Test that SSA/ASS style field is preserved during serialization."""
        # Create a test ASS file content with custom styles
        ass_content = b"""[Script Info]
Title: Test Subtitle
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CustomStyle,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1
Style: Default,Arial,16,&H00FFFFFF,&H000088EE,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:09.25,0:00:12.64,CustomStyle,,0,0,0,,First line with custom style.
Dialogue: 0,0:00:15.00,0:00:18.00,Default,,0,0,0,,Second line with default style.
"""

        # Parse the content
        store = self.StoreClass()
        store.parse(ass_content)

        # Check that units have the correct style metadata
        assert len(store.units) == 2
        assert store.units[0]._ssa_style == "CustomStyle"
        assert store.units[1]._ssa_style == "Default"

        # Serialize and check that style is preserved
        serialized = bytes(store)
        serialized_str = serialized.decode("utf-8")

        # Verify CustomStyle is preserved in the dialogue lines
        assert "CustomStyle" in serialized_str
        # Check the dialogue line specifically has CustomStyle, not Default
        lines = serialized_str.split("\n")
        dialogue_lines = [line for line in lines if line.startswith("Dialogue:")]
        assert len(dialogue_lines) == 2
        assert "CustomStyle" in dialogue_lines[0]
        assert "First line with custom style." in dialogue_lines[0]


class TestSubStationAlphaFile(TestSubRipFile):
    StoreClass = subtitles.SubStationAlphaFile

    def test_style_preservation(self) -> None:
        """Test that SSA style field is preserved during serialization."""
        # Create a test SSA file content with custom styles
        ssa_content = b"""[Script Info]
Title: Test Subtitle
ScriptType: v4.00

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: CustomStyle,Arial,20,16777215,65535,65535,0,-1,0,1,2,0,2,30,30,30,0,0
Style: Default,Arial,16,16777215,58862,16777215,0,-1,0,1,2,0,2,30,30,30,0,0

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: Marked=0,0:00:09.25,0:00:12.64,CustomStyle,,0,0,0,,First line with custom style.
Dialogue: Marked=0,0:00:15.00,0:00:18.00,Default,,0,0,0,,Second line with default style.
"""

        # Parse the content
        store = self.StoreClass()
        store.parse(ssa_content)

        # Check that units have the correct style metadata
        assert len(store.units) == 2
        assert store.units[0]._ssa_style == "CustomStyle"
        assert store.units[1]._ssa_style == "Default"

        # Serialize and check that style is preserved
        serialized = bytes(store)
        serialized_str = serialized.decode("utf-8")

        # Verify CustomStyle is preserved in the dialogue lines
        assert "CustomStyle" in serialized_str
        # Check the dialogue line specifically has CustomStyle, not Default
        lines = serialized_str.split("\n")
        dialogue_lines = [line for line in lines if line.startswith("Dialogue:")]
        assert len(dialogue_lines) == 2
        assert "CustomStyle" in dialogue_lines[0]
        assert "First line with custom style." in dialogue_lines[0]
