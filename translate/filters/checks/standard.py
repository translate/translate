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

"""The standard set of checks for (source, target) translation pairs."""

import re

from translate.filters import decoration, helpers, prefilters, spelling
from translate.filters.checks.checker import TranslationChecker
from translate.filters.checks.exceptions import FilterFailure, SeriousFilterFailure
from translate.filters.checks.tags import intuplelist, tag_re, tagproperties
from translate.filters.decorators import cosmetic, critical, extraction, functional

# These are some regular expressions that are compiled for use in some tests

# printf syntax based on https://en.wikipedia.org/wiki/Printf which doesn't
# cover everything we leave \w instead of specifying the exact letters as
# this should capture printf types defined in other platforms.
# Extended to support Python named format specifiers and objective-C special
# "%@" format specifier
# (see https://developer.apple.com/library/mac/documentation/Cocoa/Conceptual/Strings/Articles/formatSpecifiers.html)
printf_pat = re.compile(
    r"""
        %(                          # initial %
        (?P<boost_ord>\d+)%         # boost::format style variable order, like %1%
        |
              (?:(?P<ord>\d+)\$|    # variable order, like %1$s
              \((?P<key>\w+)\))?    # Python style variables, like %(var)s
        (?P<fullvar>
            [+#'-]*                 # flags
            (?:\d+)?                # width
            (?:\.\d+)?              # precision
            (hh\|h\|l\|ll)?         # length formatting
            (?P<type>[\w@]))        # type (%s, %d, etc.)
        )""",
    re.VERBOSE,
)

anonvar_re = re.compile(r"^{[0-9]*}$")


class StandardChecker(TranslationChecker):
    """The basic test suite for source -> target translations."""

    @extraction
    def untranslated(self, str1, str2) -> bool:
        """
        Checks whether a string has been translated at all.

        This check is really only useful if you want to extract untranslated
        strings so that they can be translated independently of the main work.
        """
        str2 = prefilters.removekdecomments(str2)

        return not (len(str1.strip()) > 0 and len(str2) == 0)

    @functional
    def unchanged(self, str1, str2) -> bool:
        """
        Checks whether a translation is basically identical to the original
        string.

        This checks to see if the translation isn’t just a copy of the English
        original. Sometimes, this is what you want, but other times you will
        detect words that should have been translated.
        """
        str1 = self.filteraccelerators(self.removevariables(str1)).strip()
        str2 = self.filteraccelerators(self.removevariables(str2)).strip()

        if len(str1) < 2:
            return True

        # If the whole string is upperase, or nothing in the string can go
        # towards uppercase, let's assume there is nothing translatable
        # TODO: reconsider
        if (str1.isupper() or str1.upper() == str1) and str1 == str2:
            return True

        if self.config.notranslatewords:
            words1 = str1.split()
            if len(words1) == 1 and [
                word for word in words1 if word in self.config.notranslatewords
            ]:
                # currently equivalent to:
                #   if len(words1) == 1 and words1[0] in self.config.notranslatewords:
                # why do we only test for one notranslate word?
                return True

        # we could also check for things like str1.isnumeric(), but the test
        # above (str1.upper() == str1) makes this unnecessary
        if str1.lower() == str2.lower():
            raise FilterFailure("Consider translating")

        return True

    @functional
    def blank(self, str1, str2) -> bool:
        """
        Checks whether a translation is totally blank.

        This will check to see if a translation has inadvertently been
        translated as blank i.e. as spaces. This is different from untranslated
        which is completely empty. This test is useful in that if something is
        translated as "  " it will appear to most tools as if it is translated.
        """
        len1 = len(str1.strip())
        len2 = len(str2.strip())

        if len1 > 0 and len(str2) != 0 and len2 == 0:
            raise FilterFailure("Translation is empty")
        return True

    @functional
    def short(self, str1, str2) -> bool:
        """
        Checks whether a translation is much shorter than the original
        string.

        This is most useful in the special case where the translation is 1
        characters long while the source text is multiple characters long.
        Otherwise, we use a general ratio that will catch very big differences
        but is set conservatively to limit the number of false positives.
        """
        len1 = len(str1.strip())
        len2 = len(str2.strip())

        if ((len1 > 0) and (0 < len2 < (len1 * 0.1))) or ((len1 > 1) and (len2 == 1)):
            raise FilterFailure("The translation is much shorter than the original")
        return True

    @functional
    def long(self, str1, str2) -> bool:
        """
        Checks whether a translation is much longer than the original
        string.

        This is most useful in the special case where the translation is
        multiple characters long while the source text is only 1 character
        long. Otherwise, we use a general ratio that will catch very big
        differences but is set conservatively to limit the number of false
        positives.
        """
        len1 = len(str1.strip())
        len2 = len(str2.strip())

        if ((len1 > 0) and (0 < len1 < (len2 * 0.1))) or ((len1 == 1) and (len2 > 1)):
            raise FilterFailure("The translation is much longer than the original")
        return True

    @critical
    def escapes(self, str1, str2) -> bool:
        r"""
        Checks whether escaping is consistent between the two strings.

        Checks escapes such as ``\\n`` ``\u0000`` to ensure that if they exist
        in the original string you also have them in the translation.
        """
        if not helpers.countsmatch(str1, str2, ("\\", "\\\\")):
            escapes1 = ", ".join(f"'{word}'" for word in str1.split() if "\\" in word)
            escapes2 = ", ".join(f"'{word}'" for word in str2.split() if "\\" in word)

            raise SeriousFilterFailure(
                f"Escapes in original ({escapes1}) don't match "
                f"escapes in translation ({escapes2})"
            )
        return True

    @critical
    def newlines(self, str1, str2) -> bool:
        r"""
        Checks whether newlines are consistent between the two strings.

        Counts the number of ``\\n`` newlines (and variants such as ``\\r\\n``)
        and reports and error if they differ.
        """
        if not helpers.countsmatch(str1, str2, ("\n", "\r")):
            raise FilterFailure("Different line endings")

        if str1.endswith("\n") and not str2.endswith("\n"):
            raise FilterFailure("Newlines different at end")

        if str1.startswith("\n") and not str2.startswith("\n"):
            raise FilterFailure("Newlines different at beginning")

        return True

    @critical
    def tabs(self, str1, str2) -> bool:
        r"""
        Checks whether tabs are consistent between the two strings.

        Counts the number of ``\\t`` tab markers and reports an error if they
        differ.
        """
        if not helpers.countmatch(str1, str2, "\t"):
            raise SeriousFilterFailure("Different tabs")
        return True

    @cosmetic
    def singlequoting(self, str1, str2) -> bool:
        """
        Checks whether singlequoting is consistent between the two strings.

        The same as doublequoting but checks for the ``'`` character. Because
        this is used in contractions like it's and in possessive forms like
        user's, this test can output spurious errors if your language doesn't
        use such forms. If a quote appears at the end of a sentence in the
        translation, i.e. ``'.``, this might not be detected properly by the
        check.
        """
        str1 = self.filterwordswithpunctuation(
            self.filteraccelerators(self.filtervariables(str1))
        )
        str1 = self.config.lang.punctranslate(str1)

        str2 = self.filterwordswithpunctuation(
            self.filteraccelerators(self.filtervariables(str2))
        )

        if helpers.countsmatch(str1, str2, ("'", "''", "\\'")):
            return True
        raise FilterFailure("Different quotation marks")

    @cosmetic
    def doublequoting(self, str1, str2) -> bool:
        """
        Checks whether doublequoting is consistent between the two strings.

        Checks on double quotes ``"`` to ensure that you have the same number
        in both the original and the translated string. This tests takes into
        account that several languages use different quoting characters, and
        will test for them instead.
        """
        str1 = self.filteraccelerators(self.filtervariables(str1))
        str1 = self.filterxml(str1)
        str1 = self.config.lang.punctranslate(str1)

        str2 = self.filteraccelerators(self.filtervariables(str2))
        str2 = self.filterxml(str2)

        if helpers.countsmatch(str1, str2, ('"', '""', '\\"', "«", "»", "“", "”")):
            return True
        raise FilterFailure("Different quotation marks")

    @cosmetic
    def doublespacing(self, str1, str2) -> bool:
        """
        Checks for bad double-spaces by comparing to original.

        This will identify if you have [space][space] in when you don't have it
        in the original or it appears in the original but not in your
        translation. Some of these are spurious and how you correct them
        depends on the conventions of your language.
        """
        str1 = self.filteraccelerators(str1)
        str2 = self.filteraccelerators(str2)

        if helpers.countmatch(str1, str2, "  "):
            return True
        raise FilterFailure("Different use of double spaces")

    @cosmetic
    def puncspacing(self, str1, str2) -> bool:
        """
        Checks for bad spacing after punctuation.

        In the case of [full-stop][space] in the original, this test checks
        that your translation does not remove the space. It checks also for
        [comma], [colon], etc.

        Some languages don't use spaces after common punctuation marks,
        especially where full-width punctuation marks are used. This check will
        take that into account.
        """
        # Convert all nbsp to space, and just check spaces. Useful intermediate
        # step to stricter nbsp checking?
        str1 = self.filteraccelerators(self.filtervariables(str1))
        str1 = self.config.lang.punctranslate(str1)
        str1 = str1.replace("\u00a0", " ")

        if str1.find(" ") == -1:
            return True

        str2 = self.filteraccelerators(self.filtervariables(str2))
        # Substitute: nbsp
        str2 = str2.replace("\u00a0", " ")
        # Strip: Bidi markers and ZW* chars
        str2 = str2.translate(
            {
                ord(c): None
                for c in (
                    # Bidi markers
                    "\u200e",  # LRM
                    "\u200f",  # RLM
                    "\u202b",  # RLE
                    "\u202a",  # LRE
                    "\u202e",  # RLO
                    "\u202d",  # LRO
                    "\u202c",  # PDF
                    "\u2069",  # PDI
                    "\u2068",  # FSI
                    "\u2067",  # RLI
                    "\u2066",  # LRI
                    # ZW*
                    "\u200d",  # ZWJ
                    "\u200c",  # ZWNJ
                )
            }
        )

        for puncchar in self.config.punctuation:
            plaincount1 = str1.count(puncchar)

            if not plaincount1:
                continue

            plaincount2 = str2.count(puncchar)

            if plaincount1 != plaincount2:
                continue

            spacecount1 = str1.count(f"{puncchar} ")
            spacecount2 = str2.count(f"{puncchar} ")

            if spacecount1 != spacecount2:
                # Handle extra spaces that are because of transposed punctuation

                if abs(spacecount1 - spacecount2) == 1 and str1.endswith(
                    puncchar
                ) != str2.endswith(puncchar):
                    continue

                raise FilterFailure("Different spacing around punctuation")

        return True

    @critical
    def printf(self, str1, str2) -> int:
        """
        Checks whether printf format strings match.

        If the printf formatting variables are not identical, then this will
        indicate an error. Printf statements are used by programs to format
        output in a human readable form (they are placeholders for variable
        data). They allow you to specify lengths of string variables, string
        padding, number padding, precision, etc. Generally they will look like
        this: ``%d``, ``%5.2f``, ``%100s``, etc. The test can also manage
        variables-reordering using the ``%1$s`` syntax. The variables' type and
        details following data are tested to ensure that they are strictly
        identical, but they may be reordered.

        .. seealso:: :wp:`printf Format String <Printf_format_string>`
        """
        count1 = count2 = plural = None

        # self.hasplural only set by run_filters, not always available
        if "hasplural" in self.__dict__:
            plural = self.hasplural

        for var_num2, match2 in enumerate(printf_pat.finditer(str2)):
            count2 = var_num2 + 1
            str2ord = (
                match2.group("ord")
                if not match2.group("boost_ord")
                else match2.group("boost_ord")
            )
            str2key = match2.group("key")
            str2fullvar = (
                match2.group("fullvar") if not match2.group("boost_ord") else "%"
            )

            if str2ord:
                str1ord = None
                gotmatch = False

                for var_num1, match1 in enumerate(printf_pat.finditer(str1)):
                    count1 = var_num1 + 1
                    localstr1ord = (
                        match1.group("ord")
                        if not match1.group("boost_ord")
                        else match1.group("boost_ord")
                    )

                    if localstr1ord:
                        if str2ord == localstr1ord:
                            str1ord = str2ord
                            str1fullvar = (
                                match1.group("fullvar")
                                if not match1.group("boost_ord")
                                else "%"
                            )

                            if str2fullvar == str1fullvar:
                                gotmatch = True
                    elif int(str2ord) == var_num1 + 1:
                        str1ord = str2ord
                        str1fullvar = (
                            match1.group("fullvar")
                            if not match1.group("boost_ord")
                            else "%"
                        )

                        if str2fullvar == str1fullvar:
                            gotmatch = True

                if str1ord is None:
                    raise FilterFailure(f"Added printf variable: {match2.group()}")

                if not gotmatch:
                    raise FilterFailure(f"Different printf variable: {match2.group()}")
            elif str2key:
                str1key = None

                for var_num1, match1 in enumerate(printf_pat.finditer(str1)):
                    count1 = var_num1 + 1
                    str1fullvar = (
                        match1.group("fullvar")
                        if not match1.group("boost_ord")
                        else "%"
                    )

                    if match1.group("key") and str2key == match1.group("key"):
                        str1key = match1.group("key")

                        # '%.0s' "placeholder" in plural will match anything
                        if plural and str2fullvar == ".0s":
                            continue

                        if str1fullvar != str2fullvar:
                            raise FilterFailure(
                                f"Different printf variable: {match2.group()}"
                            )

                if str1key is None:
                    raise FilterFailure(f"Added printf variable: {match2.group()}")
            else:
                for var_num1, match1 in enumerate(printf_pat.finditer(str1)):
                    count1 = var_num1 + 1
                    str1fullvar = (
                        match1.group("fullvar")
                        if not match1.group("boost_ord")
                        else "%"
                    )

                    # '%.0s' "placeholder" in plural will match anything
                    if plural and str2fullvar == ".0s":
                        continue

                    if (var_num1 == var_num2) and (str1fullvar != str2fullvar):
                        raise FilterFailure(
                            f"Different printf variable: {match2.group()}"
                        )

        if count2 is None:
            str1_variables = [m.group() for m in printf_pat.finditer(str1)]

            if str1_variables:
                raise FilterFailure(
                    f"Missing printf variable: {', '.join(str1_variables)}"
                )

        if (count1 or count2) and (count1 != count2):
            raise FilterFailure("Different number of printf variables")

        return 1

    @critical
    def pythonbraceformat(self, str1, str2) -> int:
        """Checks whether python brace format strings match."""

        # Helper function
        def max_anons(anons):
            """
            Takes a list of anonymous placeholder variables, e.g.
            ['', '1', ...]
            Determines how many anonymous formatting args the string
            they come from requires. Motivation for this function:
              * max_anons(vars_from_original) tells us how many
                anonymous placeholders are supported (at least).
              * max_anons(vars_from_translation) should not
                exceed it.
            """
            # implicit_n: you need at least as many anonymous args as
            # there are anonymous placeholders.
            implicit_n = anons.count("")
            # explicit_n: you need at least as many anonymous args as
            # the highest '{99}'-style placeholder. (The `+ 1` is to
            # correct for 0-indexing)
            try:
                explicit_n = max(
                    int(numbered_anon) + 1
                    for numbered_anon in anons
                    if len(numbered_anon) >= 1
                )
            except ValueError:
                explicit_n = 0

            return max(implicit_n, explicit_n)

        messages = []
        # Possible failure states: 0 = ok, 1 = mild, 2 = serious
        STATE_OK, STATE_MILD, STATE_SERIOUS = 0, 1, 2
        failure_state = STATE_OK
        pythonbraceformat_pat = re.compile(r"{[^}]*}")
        data1 = {}
        data2 = {}

        # Populate the data1 and data2 dicts.
        for data_, str_ in [(data1, str1), (data2, str2)]:
            # Remove all escaped braces {{ and }}
            data_["strclean"] = re.sub(r"{{|}}", "", str_)
            data_["allvars"] = pythonbraceformat_pat.findall(data_["strclean"])
            data_["anonvars"] = [
                var[1:-1] for var in data_["allvars"] if anonvar_re.match(var)
            ]
            data_["namedvars"] = [
                var for var in data_["allvars"] if not anonvar_re.match(var)
            ]

        max1 = max_anons(data1["anonvars"])
        max2 = max_anons(data2["anonvars"])

        if max1 < max2:
            failure_state = max(failure_state, STATE_SERIOUS)
            messages.append(
                f"Translation requires {max2} anonymous formatting args, original only {max1}"
            )
        elif max1 > max2:
            failure_state = max(failure_state, STATE_MILD)
            messages.append(
                f"Highest anonymous placeholder in original is {max1}, in translation {max2}"
            )

        extra_in_2 = set(data2["namedvars"]).difference(set(data1["namedvars"]))
        if len(extra_in_2) > 0:
            failure_state = max(failure_state, STATE_SERIOUS)
            messages.append(
                f"Unknown named placeholders in translation: {', '.join(extra_in_2)}"
            )

        extra_in_1 = set(data1["namedvars"]).difference(set(data2["namedvars"]))
        if len(extra_in_1) > 0:
            failure_state = max(failure_state, STATE_MILD)
            messages.append(
                f"Named placeholders absent in translation: {', '.join(extra_in_1)}"
            )

        if failure_state == STATE_OK:
            return 1
        if failure_state == STATE_MILD:
            raise FilterFailure(messages)
        if failure_state == STATE_SERIOUS:
            raise SeriousFilterFailure(messages)
        raise ValueError(
            "Something wrong in python brace checks: unreachable state reached"
        )

    @functional
    def accelerators(self, str1, str2) -> bool:
        """
        Checks whether accelerators are consistent between the two strings.

        This test is capable of checking the different type of accelerators
        that are used in different projects, like Mozilla or KDE. The test will
        pick up accelerators that are missing and ones that shouldn't be there.

        See `accelerators on the localization guide
        <https://docs.translatehouse.org/projects/localization-guide/en/latest/guide/translation/accelerators.html>`_
        for a full description on accelerators.
        """
        str1 = self.filtervariables(str1)
        str2 = self.filtervariables(str2)
        messages = []

        for accelmarker in self.config.accelmarkers:
            counter1 = decoration.countaccelerators(
                accelmarker, self.config.sourcelang.validaccel
            )
            counter2 = decoration.countaccelerators(
                accelmarker, self.config.lang.validaccel
            )
            count1, _countbad1 = counter1(str1)
            count2, countbad2 = counter2(str2)
            getaccel = decoration.getaccelerators(
                accelmarker, self.config.lang.validaccel
            )
            _accel2, bad2 = getaccel(str2)

            if count1 == count2:
                continue

            if count1 == 1 and count2 == 0:
                if countbad2 == 1:
                    messages.append(
                        f"Accelerator '{accelmarker}' appears before an invalid "
                        f"accelerator character '{bad2[0]}'"
                    )
                else:
                    messages.append(f"Missing accelerator '{accelmarker}'")
            elif count1 == 0:
                messages.append(f"Added accelerator '{accelmarker}'")
            elif count1 == 1 and count2 > count1:
                messages.append(
                    f"Accelerator '{accelmarker}' is repeated in translation"
                )
            else:
                messages.append(
                    f"Accelerator '{accelmarker}' occurs {count1} time(s) in original and {count2} time(s) in translation"
                )

        if messages:
            if "accelerators" in self.config.criticaltests:
                raise SeriousFilterFailure(messages)
            raise FilterFailure(messages)

        return True

    #    def acceleratedvariables(self, str1, str2):
    #        """checks that no variables are accelerated"""
    #        messages = []
    #        for accelerator in self.config.accelmarkers:
    #            for variablestart, variableend in self.config.varmatches:
    #                error = accelerator + variablestart
    #                if str1.find(error) >= 0:
    #                    messages.append("original has an accelerated variable")
    #                if str2.find(error) >= 0:
    #                    messages.append("translation has an accelerated variable")
    #        if messages:
    #            raise FilterFailure(messages)
    #        return True

    @critical
    def variables(self, str1, str2) -> bool:
        """
        Checks whether variables of various forms are consistent between the
        two strings.

        This checks to make sure that variables that appear in the original
        also appear in the translation. It can handle variables from projects
        like KDE or OpenOffice. It does not at the moment cope with variables
        that use the reordering syntax of Gettext PO files.
        """
        messages = []
        mismatch1, mismatch2 = [], []
        varnames1, varnames2 = [], []

        def redecorate(startmaker, endmaker, var):
            if startmarker and endmarker:
                if isinstance(endmarker, int):
                    return startmarker + var
                return startmarker + var + endmarker
            if startmarker:
                return startmarker + var
            return var

        for startmarker, endmarker in self.config.varmatches:
            varchecker = decoration.getvariables(startmarker, endmarker)

            vars1 = varchecker(str1)
            vars2 = varchecker(str2)

            if vars1 != vars2:
                # we use counts to compare so we can handle multiple variables
                vars1 = [var for var in vars1 if vars1.count(var) > vars2.count(var)]
                vars2 = [var for var in vars2 if vars1.count(var) < vars2.count(var)]
                # filter variable names we've already seen, so they aren't
                # matched by more than one filter...
                vars1 = [var for var in vars1 if var not in varnames1]
                vars2 = [var for var in vars2 if var not in varnames2]

                varnames1.extend(vars1)
                varnames2.extend(vars2)

                vars1 = [redecorate(startmarker, endmarker, var) for var in vars1]
                vars2 = [redecorate(startmarker, endmarker, var) for var in vars2]

                mismatch1.extend(vars1)
                mismatch2.extend(vars2)

        if mismatch1:
            messages.append(f"Do not translate: {', '.join(mismatch1)}")
        elif mismatch2:
            messages.append(f"Added variables: {', '.join(mismatch2)}")

        if messages and mismatch1:
            raise SeriousFilterFailure(messages)
        if messages:
            raise FilterFailure(messages)

        return True

    @functional
    def functions(self, str1, str2) -> bool:
        """
        Checks that function names are not translated.

        Checks that function names e.g. ``rgb()`` or ``getEntity.Name()`` are
        not translated.
        """
        # We can't just use helpers.funcmatch() since it doesn't ignore order
        if not set(decoration.getfunctions(str1)).symmetric_difference(
            set(decoration.getfunctions(str2))
        ):
            return True
        raise FilterFailure("Different functions")

    @functional
    def emails(self, str1, str2) -> bool:
        """
        Checks that emails are not translated.

        Generally you should not be translating email addresses. This check
        will look to see that email addresses e.g. ``info@example.com`` are not
        translated. In some cases of course you should translate the address
        but generally you shouldn't.
        """
        if helpers.funcmatch(str1, str2, decoration.getemails):
            return True
        raise FilterFailure("Different e-mails")

    @functional
    def urls(self, str1, str2) -> bool:
        """
        Checks that URLs are not translated.

        This checks only basic URLs (http, ftp, mailto etc.) not all URIs (e.g.
        afp, smb, file). Generally, you don't want to translate URLs, unless
        they are example URLs (http://your_server.com/filename.html). If the
        URL is for configuration information, then you need to query the
        developers about placing configuration information in PO files. It
        shouldn't really be there, unless it is very clearly marked: such
        information should go into a configuration file.
        """
        if helpers.funcmatch(str1, str2, decoration.geturls):
            return True
        raise FilterFailure("Different URLs")

    @functional
    def numbers(self, str1, str2) -> bool:
        """
        Checks whether numbers of various forms are consistent between the
        two strings.

        You will see some errors where you have either written the number in
        full or converted it to the digit in your translation. Also changes in
        order will trigger this error.
        """
        str1 = self.config.lang.numbertranslate(str1)

        if helpers.countsmatch(str1, str2, decoration.getnumbers(str1)):
            return True
        raise FilterFailure("Different numbers")

    @cosmetic
    def startwhitespace(self, str1, str2) -> bool:
        """
        Checks whether whitespace at the beginning of the strings matches.

        As in endwhitespace but you will see fewer errors.
        """
        if helpers.funcmatch(str1, str2, decoration.spacestart):
            return True
        raise FilterFailure("Different whitespace at the start")

    @cosmetic
    def endwhitespace(self, str1, str2) -> bool:
        """
        Checks whether whitespace at the end of the strings matches.

        Operates the same as endpunc but is only concerned with whitespace.
        This filter is particularly useful for those strings which will
        evidently be followed by another string in the program, e.g.
        [Password: ] or [Enter your username: ]. The whitespace is an inherent
        part of the string. This filter makes sure you don't miss those
        important but otherwise invisible spaces!

        If your language uses full-width punctuation (like Chinese), the visual
        spacing in the character might be enough without an added extra space.
        """
        str1 = self.config.lang.punctranslate(str1)

        if helpers.funcmatch(str1, str2, decoration.spaceend):
            return True
        raise FilterFailure("Different whitespace at the end")

    @cosmetic
    def startpunc(self, str1, str2) -> bool:
        """
        Checks whether punctuation at the beginning of the strings match.

        Operates as endpunc but you will probably see fewer errors.
        """
        str1 = self.filterxml(
            self.filterwordswithpunctuation(
                self.filteraccelerators(self.filtervariables(str1))
            )
        )
        str1 = self.config.lang.punctranslate(str1)
        str2 = self.filterxml(
            self.filterwordswithpunctuation(
                self.filteraccelerators(self.filtervariables(str2))
            )
        )

        if helpers.funcmatch(str1, str2, decoration.puncstart, self.config.punctuation):
            return True
        raise FilterFailure("Different punctuation at the start")

    @cosmetic
    def endpunc(self, str1, str2) -> bool:
        """
        Checks whether punctuation at the end of the strings match.

        This will ensure that the ending of your translation has the same
        punctuation as the original. E.g. if it ends in :[space] then so should
        yours. It is useful for ensuring that you have ellipses [...] in all
        your translations, not simply three separate full-stops. You may pick
        up some errors in the original: feel free to keep your translation and
        notify the programmers. In some languages, characters such as ``?`` or
        ``!`` are always preceded by a space e.g. [space]? — do what your
        language customs dictate. Other false positives you will notice are,
        for example, if through changes in word-order you add "), etc. at the
        end of the sentence. Do not change these: your language word-order
        takes precedence.

        It must be noted that if you are tempted to leave out [full-stop] or
        [colon] or add [full-stop] to a sentence, that often these have been
        done for a reason, e.g. a list where fullstops make it look cluttered.
        So, initially match them with the English, and make changes once the
        program is being used.

        This check is aware of several language conventions for punctuation
        characters, such as the custom question marks for Greek and Arabic,
        Devanagari Danda, full-width punctuation for CJK languages, etc.
        Support for your language can be added easily if it is not there yet.
        """
        str1 = self.filtervariables(str1)
        str1 = self.config.lang.punctranslate(str1)
        str2 = self.filtervariables(str2)
        str1 = str1.rstrip()
        str2 = str2.rstrip()

        if helpers.funcmatch(
            str1, str2, decoration.puncend, f"{self.config.endpunctuation}:"
        ):
            return True
        raise FilterFailure("Different punctuation at the end")

    @functional
    def purepunc(self, str1, str2) -> bool:
        """
        Checks that strings that are purely punctuation are not changed.

        This extracts strings like ``+`` or ``-`` as these usually should not
        be changed.
        """
        # this test is a subset of startandend
        if decoration.ispurepunctuation(str1):
            success = str1 == str2
        else:
            success = not decoration.ispurepunctuation(str2)

        if success:
            return True
        raise FilterFailure("Consider not translating punctuation")

    @cosmetic
    def brackets(self, str1, str2) -> bool:
        """
        Checks that the number of brackets in both strings match.

        If ``([{`` or ``}])`` appear in the original this will check that the
        same number appear in the translation.
        """
        str1 = self.filtervariables(str1)
        str2 = self.filtervariables(str2)

        messages = []
        missing = []
        extra = []

        for bracket in ("[", "]", "{", "}", "(", ")"):
            count1 = str1.count(bracket)
            count2 = str2.count(bracket)

            if count2 < count1:
                missing.append(f"'{bracket}'")
            elif count2 > count1:
                extra.append(f"'{bracket}'")

        if missing:
            messages.append(f"Missing {', '.join(missing)}")

        if extra:
            messages.append(f"Added {', '.join(extra)}")

        if messages:
            raise FilterFailure(messages)

        return True

    @functional
    def sentencecount(self, str1, str2) -> bool:
        """
        Checks that the number of sentences in both strings match.

        Adds the number of sentences to see that the sentence count is the same
        between the original and translated string. You may not always want to
        use this test, if you find you often need to reformat your translation,
        because the original is badly-expressed, or because the structure of
        your language works better that way. Do what works best for your
        language: it's the meaning of the original you want to convey, not the
        exact way it was written in the English.
        """
        str1 = self.filteraccelerators(str1)
        str2 = self.filteraccelerators(str2)

        sentences1 = len(self.config.sourcelang.sentences(str1))
        sentences2 = len(self.config.lang.sentences(str2))

        if not sentences1 == sentences2:
            raise FilterFailure(
                f"Different number of sentences: {sentences1} ≠ {sentences2}"
            )

        return True

    @functional
    def options(self, str1, str2) -> bool:
        """
        Checks that command line options are not translated.

        In messages that contain command line options, such as ``--help``,
        this test will check that these remain untranslated. These could be
        translated in the future if programs can create a mechanism to allow
        this, but currently they are not translated. If the options has a
        parameter, e.g. ``--file=FILE``, then the test will check that the
        parameter has been translated.
        """
        str1 = self.filtervariables(str1)

        for word1 in str1.split():
            if word1 != "--" and word1.startswith("--") and word1[-1].isalnum():
                parts = word1.split("=")

                if parts[0] not in str2:
                    raise FilterFailure(f"Missing or translated option '{parts[0]}'")

                if len(parts) > 1 and parts[1] in str2:
                    raise FilterFailure(
                        "Consider translating parameter "
                        f"'{parts[1]}' of option '{parts[0]}'"
                    )

        return True

    @cosmetic
    def startcaps(self, str1, str2) -> bool:
        """
        Checks that the message starts with the correct capitalisation.

        After stripping whitespace and common punctuation characters, it then
        checks to see that the first remaining character is correctly
        capitalised. So, if the sentence starts with an upper-case letter, and
        the translation does not, an error is produced.

        This check is entirely disabled for many languages that don't make a
        distinction between upper and lower case. Contact us if this is not yet
        disabled for your language.
        """
        str1 = self.filteraccelerators(str1)
        str2 = self.filteraccelerators(str2)

        if len(str1) > 1 and len(str2) > 1:
            if self.config.sourcelang.capsstart(str1) == self.config.lang.capsstart(
                str2
            ):
                return True
            if self.config.sourcelang.numstart(str1) or self.config.lang.numstart(str2):
                return True
            raise FilterFailure("Different capitalization at the start")

        if len(str1) == 0 and len(str2) == 0:
            return True

        if len(str1) == 0 or len(str2) == 0:
            raise FilterFailure("Different capitalization at the start")

        return True

    @cosmetic
    def simplecaps(self, str1, str2) -> bool:
        """
        Checks the capitalisation of two strings isn't wildly different.

        This will pick up many false positives, so don't be a slave to it. It
        is useful for identifying translations that don't start with a capital
        letter (upper-case letter) when they should, or those that do when they
        shouldn't. It will also highlight sentences that have extra capitals;
        depending on the capitalisation convention of your language, you might
        want to change these to Title Case, or change them all to normal
        sentence case.
        """
        str1 = self.removevariables(str1)
        str2 = self.removevariables(str2)
        # TODO: review this. The 'I' is specific to English, so it probably
        # serves no purpose to get sourcelang.sentenceend
        str1 = re.sub(f"[^{self.config.sourcelang.sentenceend}]( I )", " i ", str1)

        capitals1 = helpers.filtercount(str1, str.isupper)
        capitals2 = helpers.filtercount(str2, str.isupper)

        alpha1 = helpers.filtercount(str1, str.isalpha)
        alpha2 = helpers.filtercount(str2, str.isalpha)

        # Capture the all caps case
        if capitals1 == alpha1:
            if capitals2 == alpha2:
                return True
            raise FilterFailure("Different capitalization")

        # some heuristic tests to try and see that the style of capitals is
        # vaguely the same
        if capitals1 in {0, 1}:
            success = capitals2 == capitals1
        elif capitals1 < len(str1) / 10:
            success = capitals2 <= len(str2) / 8
        elif len(str1) < 10:
            success = abs(capitals1 - capitals2) < 3
        elif capitals1 > len(str1) * 6 / 10:
            success = capitals2 > len(str2) * 6 / 10
        else:
            success = abs(capitals1 - capitals2) < (len(str1) + len(str2)) / 6

        if success:
            return True
        raise FilterFailure("Different capitalization")

    @functional
    def acronyms(self, str1, str2) -> bool:
        """
        Checks that acronyms that appear are unchanged.

        If an acronym appears in the original this test will check that it
        appears in the translation. Translating acronyms is a language decision
        but many languages leave them unchanged. In that case this test is
        useful for tracking down translations of the acronym and correcting
        them.
        """
        allowed = []

        for startmatch, endmatch in self.config.varmatches:
            allowed += decoration.getvariables(startmatch, endmatch)(str1)

        allowed += self.config.musttranslatewords.keys()
        str1 = self.filteraccelerators(self.filtervariables(str1))
        words = self.config.lang.words(str1)
        str2 = self.filteraccelerators(self.filtervariables(str2))

        # TODO: strip XML? - should provide better error messages
        # see mail/chrome/messanger/smime.properties.po
        # TODO: consider limiting the word length for recognising acronyms to
        # something like 5/6 characters
        acronyms = [
            word
            for word in words
            if word.isupper()
            and len(word) > 1
            and word not in allowed
            and str2.find(word) == -1
        ]

        if acronyms:
            raise FilterFailure(
                f"Consider not translating acronyms: {', '.join(acronyms)}"
            )

        return True

    @cosmetic
    def doublewords(self, str1, str2) -> bool:
        """
        Checks for repeated words in the translation.

        Words that have been repeated in a translation will be highlighted with
        this test e.g. "the the", "a a". These are generally typos that need
        correcting. Some languages may have valid repeated words in their
        structure, in that case either ignore those instances or switch this
        test off.
        """
        lastword = ""
        without_newlines = "\n".join(str2.split("\n"))
        words = (
            self.filteraccelerators(
                self.removevariables(self.filterxml(without_newlines))
            )
            .replace(".", "")
            .lower()
            .split()
        )

        for word in words:
            if word == lastword and word not in self.config.lang.validdoublewords:
                raise FilterFailure(f"The word '{word}' is repeated")
            lastword = word

        return True

    @functional
    def notranslatewords(self, str1, str2) -> bool:
        """
        Checks that words configured as untranslatable appear in the
        translation too.

        Many brand names should not be translated, this test allows you to
        easily make sure that words like: Word, Excel, Impress, Calc, etc. are
        not translated. You must specify a file containing all of the
        *no translate* words using ``--notranslatefile``.
        """
        if not self.config.notranslatewords:
            return True

        str1 = self.filtervariables(str1)
        str2 = self.filtervariables(str2)

        # The above is full of strange quotes and things in utf-8 encoding.
        # single apostrophe perhaps problematic in words like "doesn't"
        for separator in self.config.punctuation:
            str1 = str1.replace(separator, " ")
            str2 = str2.replace(separator, " ")

        words1 = self.filteraccelerators(str1).split()
        words2 = self.filteraccelerators(str2).split()
        stopwords = [
            word
            for word in words1
            if word in self.config.notranslatewords and word not in words2
        ]

        if stopwords:
            raise FilterFailure(f"Do not translate: {', '.join(stopwords)}")

        return True

    @functional
    def musttranslatewords(self, str1, str2) -> bool:
        """
        Checks that words configured as definitely translatable don't appear
        in the translation.

        If for instance in your language you decide that you must translate
        'OK' then this test will flag any occurrences of 'OK' in the
        translation if it appeared in the source string. You must specify a
        file containing all of the *must translate* words using
        ``--musttranslatefile``.
        """
        if not self.config.musttranslatewords:
            return True

        str1 = self.removevariables(str1)
        str2 = self.removevariables(str2)

        # The above is full of strange quotes and things in utf-8 encoding.
        # single apostrophe perhaps problematic in words like "doesn't"
        for separator in self.config.punctuation:
            str1 = str1.replace(separator, " ")
            str2 = str2.replace(separator, " ")

        words1 = self.filteraccelerators(str1).split()
        words2 = self.filteraccelerators(str2).split()
        stopwords = [
            word
            for word in words1
            if word.lower() in self.config.musttranslatewords and word in words2
        ]

        if stopwords:
            raise FilterFailure(f"Please translate: {', '.join(stopwords)}")

        return True

    @cosmetic
    def validchars(self, str1, str2) -> bool:
        """
        Checks that only characters specified as valid appear in the
        translation.

        Often during character conversion to and from UTF-8 you get some
        strange characters appearing in your translation. This test presents a
        simple way to try and identify such errors.

        This test will only run of you specify the ``--validcharsfile`` command
        line option. This file contains all the characters that are valid in
        your language. You must use UTF-8 encoding for the characters in the
        file.

        If the test finds any characters not in your valid characters file then
        the test will print the character together with its Unicode value
        (e.g. 002B).
        """
        if not self.config.validcharsmap:
            return True

        invalid1 = str1.translate(self.config.validcharsmap)
        invalid2 = str2.translate(self.config.validcharsmap)
        invalidchars = [
            f"'{invalidchar}' (\\u{ord(invalidchar):04x})"
            for invalidchar in invalid2
            if invalidchar not in invalid1
        ]

        if invalidchars:
            raise FilterFailure(f"Invalid characters: {', '.join(invalidchars)}")

        return True

    @functional
    def filepaths(self, str1, str2) -> bool:
        """
        Checks that file paths have not been translated.

        Checks that paths such as ``/home/user1`` have not been translated.
        Generally you do not translate a file path, unless it is being used as
        an example, e.g. ``your_user_name/path/to/filename.conf``.
        """
        for word1 in self.filteraccelerators(self.filterxml(str1)).split():
            if word1.startswith("/") and not helpers.countsmatch(str1, str2, (word1,)):
                raise FilterFailure("Different file paths")

        return True

    @critical
    def xmltags(self, str1, str2) -> bool:
        """
        Checks that XML/HTML tags have not been translated.

        This check finds the number of tags in the source string and checks
        that the same number are in the translation. If the counts don't match
        then either the tag is missing or it was mistakenly translated by the
        translator, both of which are errors.

        The check ignores tags or things that look like tags that cover the
        whole string e.g. ``<Error>`` but will produce false positives for
        things like ``An <Error> occurred`` as here ``Error`` should be
        translated. It also will allow translation of the *alt* attribute in
        e.g. ``<img src="bob.png" alt="Image description">`` or similar
        translatable attributes in OpenOffice.org help files.
        """
        tags1 = tag_re.findall(str1)

        if len(tags1) > 0:
            if (len(tags1[0]) == len(str1)) and "=" not in tags1[0]:
                return True

            tags2 = tag_re.findall(str2)
            properties1 = tagproperties(tags1, self.config.ignoretags)
            properties2 = tagproperties(tags2, self.config.ignoretags)

            filtered1 = []
            filtered2 = []

            for property1 in properties1:
                filtered1 += [intuplelist(property1, self.config.canchangetags)]

            for property2 in properties2:
                filtered2 += [intuplelist(property2, self.config.canchangetags)]

            # TODO: consider the consequences of different ordering of
            # attributes/tags
            if filtered1 != filtered2:
                raise FilterFailure("Different XML tags")
        else:
            # No tags in str1, let's just check that none were added in str2.
            # This might be useful for fuzzy strings wrongly unfuzzied.
            tags2 = tag_re.findall(str2)

            if len(tags2) > 0:
                raise FilterFailure("Added XML tags")

        return True

    @functional
    def kdecomments(self, str1, str2):
        r"""
        Checks to ensure that no KDE style comments appear in the
        translation.

        KDE style translator comments appear in PO files as
        ``"_: comment\\n"``. New translators often translate the comment. This
        test tries to identify instances where the comment has been translated.
        """
        return str2.find("\n_:") == -1 and not str2.startswith("_:")

    @extraction
    def compendiumconflicts(self, str1, str2):
        """
        Checks for Gettext compendium conflicts (#-#-#-#-#).

        When you use msgcat to create a PO compendium it will insert
        ``#-#-#-#-#`` into entries that are not consistent. If the compendium
        is used later in a message merge then these conflicts will appear in
        your translations. This test quickly extracts those for correction.
        """
        return str2.find("#-#-#-#-#") == -1

    @cosmetic
    def simpleplurals(self, str1, str2) -> bool:
        """
        Checks for English style plural(s) for you to review.

        This test will extract any message that contains words with a final
        "(s)" in the source text. You can then inspect the message, to check
        that the correct plural form has been used for your language. In some
        languages, plurals are made by adding text at the beginning of words,
        making the English style messy. In this case, they often revert to the
        plural form. This test allows an editor to check that the plurals used
        are correct. Be aware that this test may create a number of false
        positives.

        For languages with no plural forms (only one noun form) this test will
        simply test that nothing like "(s)" was used in the translation.
        """

        def numberofpatterns(string, patterns):
            number = 0

            for pattern in patterns:
                number += len(re.findall(pattern, string))

            return number

        sourcepatterns = [r"\(s\)"]
        targetpatterns = [r"\(s\)"]
        sourcecount = numberofpatterns(str1, sourcepatterns)
        targetcount = numberofpatterns(str2, targetpatterns)

        if self.config.lang.nplurals == 1:
            if targetcount:
                raise FilterFailure("Plural(s) were kept in translation")
            return True

        if sourcecount == targetcount:
            return True
        raise FilterFailure("The original uses plural(s)")

    @functional
    def spellcheck(self, str1, str2) -> bool:
        """
        Checks words that don't pass a spell check.

        This test will check for misspelled words in your translation. The test
        first checks for misspelled words in the original (usually English)
        text, and adds those to an exclusion list. The advantage of this
        exclusion is that many words that are specific to the application will
        not raise errors e.g. program names, brand names, function names.

        The checker works with `PyEnchant
        <https://pyenchant.github.io/pyenchant/>`_. You need to have PyEnchant
        installed as well as a dictionary for your language (for example, one
        of the `Hunspell <https://wiki.openoffice.org/wiki/Dictionaries>`_ or
        `aspell <https://ftp.gnu.org/gnu/aspell/dict/>`_ dictionaries). This
        test will only work if you have specified the ``--language`` option.

        The pofilter error that is created, lists the misspelled word, plus
        suggestions returned from the spell checker. That makes it easy for you
        to identify the word and select a replacement.
        """
        if not self.config.targetlanguage:
            return True

        if not spelling.available:
            return True

        # TODO: filterxml?
        str1 = self.filteraccelerators_by_list(
            self.removevariables(str1), self.config.sourcelang.validaccel
        )
        str2 = self.filteraccelerators_by_list(
            self.removevariables(str2), self.config.lang.validaccel
        )
        errors = set()

        # We cache spelling results of source texts:
        ignore1 = set(spelling.simple_check(str1, lang=self.config.sourcelang.code))

        # We cache spelling results of target texts sentence-by-sentence. This
        # way we can reuse most of the results while someone is typing a long
        # segment in Virtaal.
        sentences2 = self.config.lang.sentences(str2)
        for sentence in sentences2:
            sentence_errors = spelling.simple_check(
                sentence, lang=self.config.targetlanguage
            )
            errors.update(sentence_errors)

        errors.difference_update(ignore1, self.config.notranslatewords)

        if errors:
            messages = [f"Check the spelling of: {', '.join(errors)}"]
            raise FilterFailure(messages)

        return True

    @extraction
    def credits(self, str1, str2) -> bool:
        """
        Checks for messages containing translation credits instead of
        normal translations.

        Some projects have consistent ways of giving credit to translators by
        having a unit or two where translators can fill in their name and
        possibly their contact details. This test allows you to find these
        units easily to check that they are completed correctly and also
        disables other tests that might incorrectly get triggered for these
        units (such as urls, emails, etc.)
        """
        if str1 in self.config.credit_sources:
            raise FilterFailure("Don't translate. Just credit the translators.")
        return True

    # If the precondition filter is run and fails then the other tests listed are ignored
    preconditions = {
        "untranslated": (
            "simplecaps",
            "variables",
            "startcaps",
            "accelerators",
            "brackets",
            "endpunc",
            "acronyms",
            "xmltags",
            "startpunc",
            "endwhitespace",
            "startwhitespace",
            "escapes",
            "doublequoting",
            "singlequoting",
            "filepaths",
            "purepunc",
            "doublespacing",
            "sentencecount",
            "numbers",
            "isfuzzy",
            "isreview",
            "notranslatewords",
            "musttranslatewords",
            "emails",
            "simpleplurals",
            "urls",
            "printf",
            "pythonbraceformat",
            "tabs",
            "newlines",
            "functions",
            "options",
            "blank",
            "nplurals",
            "gconf",
            "dialogsizes",
            "validxml",
        ),
        "blank": (
            "simplecaps",
            "variables",
            "startcaps",
            "accelerators",
            "brackets",
            "endpunc",
            "acronyms",
            "xmltags",
            "startpunc",
            "endwhitespace",
            "startwhitespace",
            "escapes",
            "doublequoting",
            "singlequoting",
            "filepaths",
            "purepunc",
            "doublespacing",
            "sentencecount",
            "numbers",
            "isfuzzy",
            "isreview",
            "notranslatewords",
            "musttranslatewords",
            "emails",
            "simpleplurals",
            "urls",
            "printf",
            "pythonbraceformat",
            "tabs",
            "newlines",
            "functions",
            "options",
            "gconf",
            "dialogsizes",
            "validxml",
        ),
        "credits": (
            "simplecaps",
            "variables",
            "startcaps",
            "accelerators",
            "brackets",
            "endpunc",
            "acronyms",
            "xmltags",
            "startpunc",
            "escapes",
            "doublequoting",
            "singlequoting",
            "filepaths",
            "doublespacing",
            "sentencecount",
            "numbers",
            "emails",
            "simpleplurals",
            "urls",
            "printf",
            "pythonbraceformat",
            "tabs",
            "newlines",
            "functions",
            "options",
            "validxml",
        ),
        "purepunc": ("startcaps", "options"),
        # This is causing some problems since Python 2.6, as
        # startcaps is now seen as an important one to always execute
        # and could now be done before it is blocked by a failing
        # "untranslated" or "blank" test. This is probably happening
        # due to slightly different implementation of the internal
        # dict handling since Python 2.6. We should never have relied
        # on this ordering anyway.
        # "startcaps": ("simplecaps",),
        "endwhitespace": ("endpunc",),
        "startwhitespace": ("startpunc",),
        "unchanged": ("doublewords",),
        "compendiumconflicts": (
            "accelerators",
            "brackets",
            "escapes",
            "numbers",
            "startpunc",
            "long",
            "variables",
            "startcaps",
            "sentencecount",
            "simplecaps",
            "doublespacing",
            "endpunc",
            "xmltags",
            "startwhitespace",
            "endwhitespace",
            "singlequoting",
            "doublequoting",
            "filepaths",
            "purepunc",
            "doublewords",
            "printf",
            "newlines",
            "validxml",
        ),
    }
