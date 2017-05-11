# -*- coding: utf-8 -*-
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

"""Class that manages subtitle files for translation.

This class makes use of the subtitle functionality of ``gaupol``.

.. seealso:: gaupol/agents/open.py::open_main

A patch to gaupol is required to open utf-8 files successfully.
"""

import os
import six
import tempfile
from io import StringIO

try:
    from aeidon import Subtitle, documents, newlines
    from aeidon.encodings import detect
    from aeidon.files import (AdvSubStationAlpha, MicroDVD, SubRip,
                              SubStationAlpha, new)
    from aeidon.util import detect_format as determine
except ImportError:
    try:
        from gaupol import FormatDeterminer, documents
        from gaupol.encodings import detect
        from gaupol.files import (AdvSubStationAlpha, MicroDVD, SubRip,
                                  SubStationAlpha, new)
        from gaupol.newlines import newlines
        from gaupol.subtitle import Subtitle
        _determiner = FormatDeterminer()
        determine = _determiner.determine
    except ImportError:
        if six.PY3:
            raise ImportError('\naeidon or gaupol package required for Subtitle support')
        else:
            raise ImportError('\ngaupol package required for Subtitle support')

from translate.storage import base


class SubtitleUnit(base.TranslationUnit):
    """A subtitle entry that is translatable"""

    def __init__(self, source=None, **kwargs):
        self._start = None
        self._end = None
        if source:
            self.source = source
        super(SubtitleUnit, self).__init__(source)

    def getnotes(self, origin=None):
        if origin in ['programmer', 'developer', 'source code', None]:
            return "visible for %d seconds" % self._duration
        else:
            return ''

    def getlocations(self):
        return ["%s-->%s" % (self._start, self._end)]

    def getid(self):
        return self.getlocations()[0]


class SubtitleFile(base.TranslationStore):
    """A subtitle file"""

    UnitClass = SubtitleUnit

    def __init__(self, inputfile=None, **kwargs):
        """construct an Subtitle file, optionally reading in from inputfile."""
        super(SubtitleFile, self).__init__(**kwargs)
        self.filename = None
        self._subtitlefile = None
        if inputfile is not None:
            self._parsefile(inputfile)

    def serialize(self, out):
        subtitles = []
        for unit in self.units:
            subtitle = Subtitle()
            subtitle.main_text = unit.target or unit.source
            subtitle.start = unit._start
            subtitle.end = unit._end
            subtitles.append(subtitle)
        # Using transient output might be dropped if/when we have more control
        # over the open mode of out files.
        output = StringIO()
        self._subtitlefile.write_to_file(subtitles, documents.MAIN, output)
        out.write(output.getvalue().encode(self._subtitlefile.encoding))

    def _parse(self):
        try:
            self.encoding = detect(self.filename)
            self._format = determine(self.filename, self.encoding)
            self._subtitlefile = new(self._format, self.filename, self.encoding)
            for subtitle in self._subtitlefile.read():
                newunit = self.addsourceunit(subtitle.main_text)
                newunit._start = subtitle.start
                newunit._end = subtitle.end
                newunit._duration = subtitle.duration_seconds
        except Exception as e:
            raise base.ParseError(e)

    def _parsefile(self, storefile):
        if hasattr(storefile, 'name'):
            self.filename = storefile.name
            storefile.close()
        elif hasattr(storefile, 'filename'):
            self.filename = storefile.filename
            storefile.close()
        elif isinstance(storefile, six.string_types):
            self.filename = storefile

        if self.filename and os.path.exists(self.filename):
            self._parse()
        else:
            self.parse(storefile.read())

    @classmethod
    def parsefile(cls, storefile):
        """parse the given file"""
        newstore = cls()
        newstore._parsefile(storefile)
        return newstore

    def parse(self, input):
        if isinstance(input, bytes):
            # Gaupol does not allow parsing from strings
            if self.filename:
                tmpfile, tmpfilename = tempfile.mkstemp(suffix=self.filename)
            else:
                tmpfile, tmpfilename = tempfile.mkstemp()
            with open(tmpfilename, 'wb') as fh:
                fh.write(input)
            self._parsefile(tmpfilename)
            os.remove(tmpfilename)
        else:
            self._parsefile(input)


############# format specific classes ###################

# the generic SubtitleFile can adapt to any format, but only the
# specilized classes can be used to construct a new file


class SubRipFile(SubtitleFile):
    """specialized class for SubRipFile's only"""

    Name = "SubRip subtitles file"
    Extensions = ['srt']

    def __init__(self, *args, **kwargs):
        super(SubRipFile, self).__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = SubRip(self.filename or '', self.encoding)
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX


class MicroDVDFile(SubtitleFile):
    """specialized class for SubRipFile's only"""

    Name = "MicroDVD subtitles file"
    Extensions = ['sub']

    def __init__(self, *args, **kwargs):
        super(MicroDVDFile, self).__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = MicroDVD(self.filename or '', self.encoding)
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX


class AdvSubStationAlphaFile(SubtitleFile):
    """specialized class for SubRipFile's only"""

    Name = "Advanced Substation Alpha subtitles file"
    Extensions = ['ass']

    def __init__(self, *args, **kwargs):
        super(AdvSubStationAlphaFile, self).__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = AdvSubStationAlpha(self.filename or '', self.encoding)
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX


class SubStationAlphaFile(SubtitleFile):
    """specialized class for SubRipFile's only"""

    Name = "Substation Alpha subtitles file"
    Extensions = ['ssa']

    def __init__(self, *args, **kwargs):
        super(SubStationAlphaFile, self).__init__(*args, **kwargs)
        if self._subtitlefile is None:
            self._subtitlefile = SubStationAlpha(self.filename or '', self.encoding)
        if self._subtitlefile.newline is None:
            self._subtitlefile.newline = newlines.UNIX
