#
# Copyright 2004-2011 Zuza Software Foundation
# 2013, 2016 F Wolff
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""Exceptions raised by the checks to signal a failure."""


class FilterFailure(Exception):
    """
    This exception signals that a Filter didn't pass, and gives an
    explanation or a comment.
    """

    def __init__(self, messages: str | list[str]) -> None:
        if not isinstance(messages, list):
            messages = [messages]

        assert isinstance(messages[0], str)  # Assumption: all of same type

        self.messages = messages

    def __str__(self) -> str:
        return ", ".join(self.messages)


class SeriousFilterFailure(FilterFailure):
    """
    This exception signals that a Filter didn't pass, and the bad
    translation might break an application (so the string will be marked
    fuzzy).
    """
