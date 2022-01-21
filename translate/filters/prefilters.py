#
# Copyright 2004-2008,2010 Zuza Software Foundation
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

"""Filters that strings can be passed through before certain tests.
"""

import re

from translate.filters import decoration
from translate.misc import quote


def removekdecomments(str1):
    r"""Remove KDE-style PO comments.

    KDE comments start with ``_:[space]`` and end with a literal ``\n``.
    Example::

      "_: comment\n"
    """
    assert isinstance(str1, str)
    iskdecomment = False
    lines = str1.split("\n")
    removelines = []
    for linenum in range(len(lines)):
        line = lines[linenum]
        if line.startswith("_:"):
            lines[linenum] = ""
            iskdecomment = True
        if iskdecomment:
            removelines.append(linenum)
        if line.strip() and not iskdecomment:
            break
        if iskdecomment and line.strip().endswith("\\n"):
            iskdecomment = False
    lines = [
        lines[linenum] for linenum in range(len(lines)) if linenum not in removelines
    ]
    return "\n".join(lines)


def filteraccelerators(accelmarker):
    """Returns a function that filters accelerators marked using *accelmarker*
    from a strings.

    :param string accelmarker: Accelerator marker character
    :rtype: Function
    :return: fn(str1, acceplist=None)
    """
    if accelmarker is None:
        accelmarkerlen = 0
    else:
        accelmarkerlen = len(accelmarker)

    def filtermarkedaccelerators(str1, acceptlist=None):
        """Modifies the accelerators in *str1* marked with the given
        *accelmarker*, using a given *acceptlist* filter.
        """
        acclocs, badlocs = decoration.findaccelerators(str1, accelmarker, acceptlist)
        fstr1, pos = "", 0
        for accelstart, accelerator in acclocs:
            fstr1 += str1[pos:accelstart]
            fstr1 += accelerator
            pos = accelstart + accelmarkerlen + len(accelerator)
        fstr1 += str1[pos:]
        return fstr1

    return filtermarkedaccelerators


def varname(variable, startmarker, endmarker):
    r"""Variable filter that returns the variable name without the marking
    punctuation.

    .. note:: Currently this function simply returns *variable* unchanged, no
       matter what *\*marker*’s are set to.

    :rtype: String
    :return: Variable name with the supplied *startmarker* and *endmarker*
             removed.
    """
    return variable
    # if the punctuation were included, we'd do the following:
    if startmarker is None:
        return variable[: variable.rfind(endmarker)]
    elif endmarker is None:
        return variable[variable.find(startmarker) + len(startmarker) :]
    else:
        return variable[
            variable.find(startmarker) + len(startmarker) : variable.rfind(endmarker)
        ]


def varnone(variable, startmarker, endmarker):
    """Variable filter that returns an empty string.

    :rtype: String
    :return: Empty string
    """
    return ""


def filtervariables(startmarker, endmarker, varfilter):
    """Returns a function that filters variables marked using *startmarker* and
    *endmarker* from a string.

    :param string startmarker: Start of variable marker
    :param string endmarker: End of variable marker
    :param Function varfilter: fn(variable, startmarker, endmarker)
    :rtype: Function
    :return: fn(str1)
    """
    if startmarker is None:
        startmarkerlen = 0
    else:
        startmarkerlen = len(startmarker)
    if endmarker is None:
        endmarkerlen = 0
    elif type(endmarker) is int:
        endmarkerlen = 0
    else:
        endmarkerlen = len(endmarker)

    def filtermarkedvariables(str1):
        r"""Modifies the variables in *str1* marked with a given *\*marker*,
        using a given filter.
        """
        varlocs = decoration.findmarkedvariables(str1, startmarker, endmarker)
        fstr1, pos = "", 0
        for varstart, variable in varlocs:
            fstr1 += str1[pos:varstart]
            fstr1 += varfilter(variable, startmarker, endmarker)
            pos = varstart + startmarkerlen + len(variable) + endmarkerlen
        fstr1 += str1[pos:]
        return fstr1

    return filtermarkedvariables


# a list of special words with punctuation
# all apostrophes in the middle of the word are handled already
wordswithpunctuation = ["'n", "'t"]  # Afrikaans
# map all the words to their non-punctified equivalent
wordswithpunctuation = {
    word: "".join(filter(str.isalnum, word)) for word in wordswithpunctuation
}

word_with_apos_re = re.compile(r"(?u)\w+'\w+")


def filterwordswithpunctuation(str1):
    """Goes through a list of known words that have punctuation and removes the
    punctuation from them.
    """
    if "'" not in str1:
        return str1
    occurrences = []
    for word, replacement in wordswithpunctuation.items():
        occurrences.extend(
            [(pos, word, replacement) for pos in quote.find_all(str1, word)]
        )
    for match in word_with_apos_re.finditer(str1):
        word = match.group()
        replacement = "".join(filter(str.isalnum, word))
        occurrences.append((match.start(), word, replacement))
    occurrences.sort()
    if occurrences:
        lastpos = 0
        newstr1 = ""
        for pos, word, replacement in occurrences:
            newstr1 += str1[lastpos:pos]
            newstr1 += replacement
            lastpos = pos + len(word)
        newstr1 += str1[lastpos:]
        return newstr1
    else:
        return str1
