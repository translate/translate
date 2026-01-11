#
# Copyright 2008-2009 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Class that manages subtitle files for translation.

This class makes use of the subtitle functionality of ``aeidon``.
"""

from __future__ import annotations

import os
from io import StringIO
from tempfile import NamedTemporaryFile

from translate.storage import base

try:
    from aeidon import Subtitle, documents, formats, newlines
    from aeidon.encodings import detect
    from aeidon.files import AdvSubStationAlpha, MicroDVD, SubRip, SubStationAlpha, new
    from aeidon.util import detect_format
except ImportError as error:
    raise ImportError("\naeidon package required for Subtitle support") from error


class SubtitleUnit(base.TranslationUnit):
    """A subtitle entry that is translatable."""

    init_time = "00:00:00.000"

    def __init__(self, source: str | None = None, **kwargs) -> None:
        self._start = self.init_time
        self._end = self.init_time
        self._duration = 0.0
        self._ssa_style = None
        self._ssa_layer = None
        self._ssa_name = None
        self._ssa_margin_l = None
        self._ssa_margin_r = None
        self._ssa_margin_v = None
        self._ssa_effect = None
        if source:
            self.source = source
            self.target = source
        super().__init__(source)

    def settime(self, start: str, end: str, duration: float) -> None:
        self._start = start
        self._end = end
        self._duration = duration

    def set_ssa_metadata(
        self,
        style: str | None = None,
        layer: int | None = None,
        name: str | None = None,
        margin_l: int | None = None,
        margin_r: int | None = None,
        margin_v: int | None = None,
        effect: str | None = None,
    ) -> None:
        """Store SSA/ASS subtitle metadata (style, layer, margins, etc.)."""
        self._ssa_style = style
        self._ssa_layer = layer
        self._ssa_name = name
        self._ssa_margin_l = margin_l
        self._ssa_margin_r = margin_r
        self._ssa_margin_v = margin_v
        self._ssa_effect = effect

    def getnotes(self, origin=None) -> str:
        if origin in {"programmer", "developer", "source code", None}:
            return f"visible for {self._duration} seconds"
        return ""

    def getlocations(self):
        return [f"{self._start}-->{self._end}"]

    def getid(self):
        return self.getlocations()[0]


class MicroDVDUnit(SubtitleUnit):
    """MicroDVD unit, it uses frames instead of time as start/end."""

    init_time = 0


class SubtitleFile(base.TranslationStore):
    """A subtitle file."""

    UnitClass = SubtitleUnit

    def __init__(self, inputfile=None, **kwargs) -> None:
        """Construct an Subtitle file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = None
        self._subtitlefile = None
        self._format = None
        if inputfile is not None:
            self._parsefile(inputfile)

    def serialize(self, out) -> None:
        subtitles = []
        for unit in sorted(self.units, key=lambda unit: unit._start):
            subtitle = Subtitle()
            subtitle.main_text = unit.target or unit.source
            subtitle.start = unit._start
            subtitle.end = unit._end
            # Restore SSA/ASS metadata only for SSA and ASS formats
            if (
                self._format in {formats.SSA, formats.ASS}  # ty:ignore[unresolved-attribute]
                and hasattr(subtitle, "ssa")
                and subtitle.ssa
            ):
                if unit._ssa_style is not None:
                    subtitle.ssa.style = unit._ssa_style
                if unit._ssa_layer is not None:
                    subtitle.ssa.layer = unit._ssa_layer
                if unit._ssa_name is not None:
                    subtitle.ssa.name = unit._ssa_name
                if unit._ssa_margin_l is not None:
                    subtitle.ssa.margin_l = unit._ssa_margin_l
                if unit._ssa_margin_r is not None:
                    subtitle.ssa.margin_r = unit._ssa_margin_r
                if unit._ssa_margin_v is not None:
                    subtitle.ssa.margin_v = unit._ssa_margin_v
                if unit._ssa_effect is not None:
                    subtitle.ssa.effect = unit._ssa_effect
            subtitles.append(subtitle)
        # Using transient output might be dropped if/when we have more control
        # over the open mode of out files.
        output = StringIO()
        self._subtitlefile.write_to_file(subtitles, documents.MAIN, output)  # ty:ignore[possibly-missing-attribute, unresolved-attribute]
        out.write(output.getvalue().encode(self._subtitlefile.encoding))  # ty:ignore[possibly-missing-attribute]

    def _set_default_ssa_metadata(self, unit: SubtitleUnit) -> None:
        """Set default SSA metadata for a unit (helper for SSA/ASS subclasses)."""
        unit.set_ssa_metadata(
            style="Default",
            layer=0,
            name="",
            margin_l=0,
            margin_r=0,
            margin_v=0,
            effect="",
        )

    def _parse(self) -> None:
        try:
            self.encoding = detect(self.filename)
            self._format = detect_format(self.filename, self.encoding)
            self._subtitlefile = new(self._format, self.filename, self.encoding)
            for subtitle in self._subtitlefile.read():
                newunit = self.addsourceunit(subtitle.main_text)
                newunit._start = subtitle.start
                newunit._end = subtitle.end
                newunit._duration = subtitle.duration_seconds
                # Preserve SSA/ASS metadata only for SSA and ASS formats
                if (
                    self._format in {formats.SSA, formats.ASS}  # ty:ignore[unresolved-attribute]
                    and hasattr(subtitle, "ssa")
                    and subtitle.ssa
                ):
                    newunit.set_ssa_metadata(
                        style=subtitle.ssa.style,
                        layer=subtitle.ssa.layer,
                        name=subtitle.ssa.name,
                        margin_l=subtitle.ssa.margin_l,
                        margin_r=subtitle.ssa.margin_r,
                        margin_v=subtitle.ssa.margin_v,
                        effect=subtitle.ssa.effect,
                    )
        except Exception as e:
            raise base.ParseError(e) from e

    def _parsefile(self, storefile) -> None:
        if hasattr(storefile, "name"):
            self.filename = storefile.name
            storefile.close()
        elif hasattr(storefile, "filename"):
            self.filename = storefile.filename
            storefile.close()
        elif isinstance(storefile, str):
            self.filename = storefile

        if self.filename and os.path.exists(self.filename):
            self._parse()
        else:
            self.parse(storefile.read())

    @classmethod
    def parsefile(cls, storefile):
        """Parse the given file."""
        newstore = cls()
        newstore._parsefile(storefile)
        return newstore

    def parse(self, input) -> None:  # ty:ignore[invalid-method-override]
        if isinstance(input, bytes):
            # Gaupol does not allow parsing from strings
            kwargs = {"delete": False}
            if self.filename:
                kwargs["suffix"] = self.filename

            temp_file = NamedTemporaryFile(**kwargs)  # ty:ignore[no-matching-overload]
            temp_file.close()

            try:
                with open(temp_file.name, "wb") as fh:
                    fh.write(input)
                self._parsefile(temp_file.name)
            finally:
                os.unlink(temp_file.name)
        else:
            self._parsefile(input)


############# format specific classes ###################

# the generic SubtitleFile can adapt to any format, but only the
# specialized classes can be used to construct a new file


class SubRipFile(SubtitleFile):
    """specialized class for SubRipFile's only."""

    Name = "SubRip subtitles file"
    Extensions = ["srt"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = SubRip(self.filename or "", self.encoding)
            self._format = formats.SUBRIP  # ty:ignore[unresolved-attribute]
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX  # ty:ignore[unresolved-attribute]


class MicroDVDFile(SubtitleFile):
    """specialized class for SubRipFile's only."""

    Name = "MicroDVD subtitles file"
    Extensions = ["sub"]
    UnitClass = MicroDVDUnit

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = MicroDVD(self.filename or "", self.encoding)
            self._format = formats.MICRODVD  # ty:ignore[unresolved-attribute]
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX  # ty:ignore[unresolved-attribute]


class AdvSubStationAlphaFile(SubtitleFile):
    """specialized class for Advanced Substation Alpha files only."""

    Name = "Advanced Substation Alpha subtitles file"
    Extensions = ["ass"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = AdvSubStationAlpha(self.filename or "", self.encoding)
            self._format = formats.ASS  # ty:ignore[unresolved-attribute]
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX  # ty:ignore[unresolved-attribute]

    def addsourceunit(self, source: str) -> base.TranslationUnit:
        """Add a unit with default SSA metadata."""
        unit = super().addsourceunit(source)
        # Set default SSA metadata for manually created units
        self._set_default_ssa_metadata(unit)
        return unit


class SubStationAlphaFile(SubtitleFile):
    """specialized class for Substation Alpha files only."""

    Name = "Substation Alpha subtitles file"
    Extensions = ["ssa"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = SubStationAlpha(self.filename or "", self.encoding)
            self._format = formats.SSA  # ty:ignore[unresolved-attribute]
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX  # ty:ignore[unresolved-attribute]

    def addsourceunit(self, source: str) -> base.TranslationUnit:
        """Add a unit with default SSA metadata."""
        unit = super().addsourceunit(source)
        # Set default SSA metadata for manually created units
        self._set_default_ssa_metadata(unit)
        return unit
