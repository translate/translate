#
# Copyright 2026 Ivan Tugay <listepo@gmail.com>
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

"""
Convert Gettext PO localization files to Fluent (.ftl) files.

This is the reverse of :mod:`translate.convert.fluent2po`: a Fluent template is
filled in with the translations found in a PO file. Messages and terms are
matched by the Fluent ID stored in the PO location (``#: message-id``) or, as a
fallback, in ``msgctxt``.

A singular PO translation holds Fluent syntax, exactly as produced by
fluent2po, so select expressions, attributes and placeables are copied as is.

A gettext plural unit (``msgid_plural``/``msgstr[n]``) is turned into a Fluent
select expression. Every gettext form is mapped to CLDR plural categories by
evaluating the ``Plural-Forms`` expression of the PO header on sample integers
and classifying the same integers with the CLDR rules of the target language
(:mod:`translate.misc.cldr_plurals`). Fluent requires a default variant, which
is always ``*[other]``. When CLDR ``other`` only covers fractions (for example
in Belarusian, Polish, Russian and Ukrainian), gettext has no matching form:
``other`` then reuses the ``few`` form for Belarusian, Russian and Ukrainian,
where fractions take the genitive singular that the ``few`` form mostly
matches (``1,5 файла``), and the last gettext form otherwise.

See: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/fluent2po.html
for examples and usage instructions.
"""

from __future__ import annotations

import gettext
import logging
import re
from collections import Counter
from copy import deepcopy
from functools import cache

from fluent.syntax import ast

from translate.convert import convert
from translate.lang import data
from translate.misc import cldr_plurals
from translate.storage import fluent, po

logger = logging.getLogger(__name__)

SAMPLE_NUMBERS = (
    *range(1001),
    *range(1100, 100_001, 100),
    *range(200_000, 10_000_001, 100_000),
)
"""Integers used to match gettext plural forms with CLDR plural categories."""

FRACTION_FORMS = {"be": "few", "ru": "few", "uk": "few"}
"""
The CLDR category whose form fills ``other`` when ``other`` only covers
fractions. Other languages use the last gettext form.
"""

DEFAULT_SELECTOR = "count"

_VARIABLE_RE = re.compile(r"{\s*\$([a-zA-Z][a-zA-Z0-9_-]*)")
_PLURAL_FORMS_RE = re.compile(r"nplurals\s*=\s*(\d+)\s*;\s*plural\s*=(.+?);?")


class PluralFormsError(ValueError):
    """The plural forms of a PO file cannot be mapped to CLDR categories."""


def gettext_plural_forms(value: str) -> tuple[int, str]:
    """
    Parse the value of a gettext ``Plural-Forms`` header.

    :return: A ``(nplurals, plural)`` tuple.
    :raises ValueError: if the value or the plural expression is invalid.
    """
    match = _PLURAL_FORMS_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Invalid Plural-Forms header: {value}")
    plural = match.group(2).strip()
    gettext.c2py(plural)
    return int(match.group(1)), plural


def get_plural_forms(
    store: po.pofile,
) -> tuple[str | None, int | None, str | None]:
    """
    Get the target language and the gettext plural forms of a PO file.

    The Plural-Forms header is used when valid; otherwise the gettext plural
    forms known by :mod:`translate.lang.data` for the language are used.

    :return: A ``(language, nplurals, plural)`` tuple, where ``nplurals`` and
        ``plural`` are None if they are unknown.
    """
    language = store.gettargetlanguage() or None
    value = store.parseheader().get("Plural-Forms")
    if value:
        try:
            nplurals, plural = gettext_plural_forms(value)
        except ValueError:
            logger.warning("Invalid Plural-Forms header: %s", value)
        else:
            return language, nplurals, plural
    if language:
        for code in (language, re.split(r"[_@.-]", language)[0]):
            if code in data.languages:
                _name, nplurals, plural = data.languages[code]
                return language, nplurals, plural
    return language, None, None


@cache
def _classify_samples(code: str, nplurals: int, plural: str) -> dict[str, Counter[int]]:
    """Count the gettext forms used by the sample integers of each category."""
    expression = gettext.c2py(plural)
    forms: dict[str, Counter[int]] = {}
    for number in SAMPLE_NUMBERS:
        index = expression(number)
        if not 0 <= index < nplurals:
            raise PluralFormsError(
                f"Plural expression {plural} gives form {index} for {number}, "
                f"but nplurals={nplurals}"
            )
        category = cldr_plurals.get_category(code, number)
        forms.setdefault(category, Counter())[index] += 1
    return forms


def get_plural_mapping(
    language: str | None, nplurals: int, plural: str
) -> dict[str, int]:
    """
    Map CLDR plural categories of *language* to gettext plural form indexes.

    Each gettext form is evaluated on :data:`SAMPLE_NUMBERS`, and a CLDR
    category gets the form used by most integers of that category. The
    ``other`` category is always present, see :data:`FRACTION_FORMS`.

    :return: An ordered dict ``{category: index}`` in CLDR order.
    :raises PluralFormsError: if the language or the expression is unknown or
        invalid.
    """
    try:
        gettext.c2py(plural)
    except ValueError as error:
        raise PluralFormsError(f"Invalid plural expression: {plural}") from error
    if nplurals < 1:
        raise PluralFormsError(f"Invalid nplurals: {nplurals}")
    code = cldr_plurals.normalize_language(language)
    if code is None:
        if nplurals == 1:
            return {"other": 0}
        raise PluralFormsError(f"Unknown CLDR plural rules for language {language!r}")

    forms = _classify_samples(code, nplurals, plural)
    mapping = {}
    for category in cldr_plurals.get_categories(code):
        if category in forms:
            (index, _count), *others = forms[category].most_common()
            if others:
                logger.warning(
                    "Plural category %s of %s is split over gettext forms %s, "
                    "using form %d",
                    category,
                    code,
                    sorted(forms[category]),
                    index,
                )
            mapping[category] = index
        elif category == "other":
            fraction_category = FRACTION_FORMS.get(code.split("-")[0])
            mapping[category] = mapping.get(fraction_category, nplurals - 1)
        # Other categories that only contain fractions (such as "many" in
        # Czech) are left to the default variant.

    unused = sorted(set(range(nplurals)) - set(mapping.values()))
    if unused:
        logger.warning(
            "Gettext plural forms %s are not used by any CLDR category of %s",
            unused,
            code,
        )
    return mapping


def _parse_pattern(text: str) -> ast.Pattern:
    """Parse a Fluent pattern, as found in a gettext plural form."""
    entry = fluent.FluentUnit(source=text, unit_id="plural-form").to_entry()
    if entry is None or entry.value is None or entry.attributes:  # ty:ignore[unresolved-attribute]
        raise fluent.FluentContentError(
            f"Plural form is not a Fluent pattern without attributes: {text!r}"
        )
    return entry.value  # ty:ignore[unresolved-attribute]


def _template_selector(entry: ast.Message | ast.Term) -> ast.InlineExpression | None:
    """Find the selector of a plural select expression in a template entry."""
    if entry.value is None:
        return None
    for element in entry.value.elements:
        if not isinstance(element, ast.Placeable):
            continue
        expression = element.expression
        if not isinstance(expression, ast.SelectExpression):
            continue
        for variant in expression.variants:
            key = variant.key
            if isinstance(key, ast.NumberLiteral) or (
                isinstance(key, ast.Identifier) and key.name in cldr_plurals.CATEGORIES
            ):
                return deepcopy(expression.selector)
    return None


def _selector_from_strings(*texts: str) -> ast.InlineExpression:
    """Guess the variable holding the number from the PO strings."""
    for text in texts:
        match = _VARIABLE_RE.search(text)
        if match:
            return ast.VariableReference(ast.Identifier(match.group(1)))
    return ast.VariableReference(ast.Identifier(DEFAULT_SELECTOR))


class po2fluent:
    """Convert a PO file to a Fluent file, using a Fluent template."""

    def __init__(self, includefuzzy: bool = False) -> None:
        self.includefuzzy = includefuzzy
        self.language: str | None = None
        self.nplurals: int | None = None
        self.plural: str | None = None
        self.mapping: dict[str, int] | None = None

    def convert_store(
        self, template_store: fluent.FluentFile, input_store: po.pofile
    ) -> fluent.FluentFile:
        """Fill *template_store* with the translations of *input_store*."""
        self.language, self.nplurals, self.plural = get_plural_forms(input_store)
        self.mapping = None
        by_location: dict[str, po.pounit] = {}
        by_context: dict[str, po.pounit] = {}
        for unit in input_store.units:
            if unit.isheader() or unit.isobsolete():
                continue
            for location in unit.getlocations():
                by_location.setdefault(location, unit)
            context = unit.getcontext()
            if context:
                by_context.setdefault(context, unit)

        for template_unit in template_store.units:
            if template_unit.isheader() or not template_unit.istranslatable():
                continue
            unit_id = template_unit.getid()
            input_unit = by_location.get(unit_id) or by_context.get(unit_id)
            if input_unit is None or not self.should_use(input_unit):
                continue
            try:
                translation = self.convert_unit(template_unit, input_unit)
            except (fluent.FluentContentError, PluralFormsError) as error:
                logger.warning(
                    "Using the template for %s, the translation cannot be "
                    "converted: %s",
                    unit_id,
                    error,
                )
                continue
            template_unit.source = translation
            template_unit.target = translation
        return template_store

    def should_use(self, unit: po.pounit) -> bool:
        """Whether the translation of *unit* is used, instead of the template."""
        if unit.isfuzzy() and not self.includefuzzy:
            return False
        if unit.hasplural():
            return all(str(text) for text in unit.target.strings)
        return bool(unit.target)

    def convert_unit(
        self, template_unit: fluent.FluentUnit, input_unit: po.pounit
    ) -> str:
        """
        Convert the translation of *input_unit* to the source of a Fluent unit.

        :raises fluent.FluentContentError: if the translation is not valid
            Fluent.
        :raises PluralFormsError: if the plural forms cannot be mapped.
        """
        if input_unit.hasplural():
            return self.convert_plural(template_unit, input_unit)
        translation = str(input_unit.target)
        checked = fluent.FluentUnit(
            source=translation,
            unit_id=template_unit.getid(),
            fluent_type=template_unit.fluent_type,
        )
        error = checked.get_syntax_error()
        if error:
            raise fluent.FluentContentError(error)
        return translation

    def convert_plural(
        self, template_unit: fluent.FluentUnit, input_unit: po.pounit
    ) -> str:
        """Convert gettext plural forms to a Fluent select expression."""
        if self.nplurals is None or self.plural is None:
            raise PluralFormsError(
                f"Unknown plural forms for language {self.language!r}, "
                "please set the Plural-Forms header"
            )
        if self.mapping is None:
            self.mapping = get_plural_mapping(self.language, self.nplurals, self.plural)
        mapping = self.mapping
        forms = [str(text) for text in input_unit.target.strings]
        if len(forms) < self.nplurals:
            raise PluralFormsError(
                f"Found {len(forms)} plural forms, but nplurals={self.nplurals}"
            )
        if len(forms) > self.nplurals:
            logger.warning(
                "Ignoring %d extra plural forms of %s (nplurals=%d)",
                len(forms) - self.nplurals,
                template_unit.getid(),
                self.nplurals,
            )

        template_entry = template_unit.to_entry()
        unit_id = template_unit.getid()
        assert isinstance(template_entry, (ast.Message, ast.Term))
        assert unit_id is not None
        patterns = {
            index: _parse_pattern(forms[index]) for index in set(mapping.values())
        }
        if len(mapping) == 1:
            value = deepcopy(patterns[mapping["other"]])
        else:
            selector = _template_selector(template_entry) or _selector_from_strings(
                *input_unit.source.strings, *forms
            )
            variants = [
                ast.Variant(
                    key=ast.Identifier(category),
                    value=deepcopy(patterns[index]),
                    default=category == "other",
                )
                for category, index in mapping.items()
            ]
            value = ast.Pattern(
                [ast.Placeable(ast.SelectExpression(selector, variants))]
            )

        entry_class = ast.Term if template_unit.fluent_type == "Term" else ast.Message
        entry = entry_class(
            id=ast.Identifier(unit_id.removeprefix("-")),
            value=value,
            attributes=deepcopy(template_entry.attributes),
        )
        return fluent.FluentUnit.new_from_entry(entry).source


def convertfluent(
    inputfile, outputfile, templatefile, includefuzzy=False, outputthreshold=None
) -> int:
    """
    Reads in *inputfile* using po, fills *templatefile* with the translations
    using :class:`po2fluent`, and writes the Fluent file to *outputfile*.
    """
    inputstore = po.pofile(inputfile)
    if not convert.should_output_store(inputstore, outputthreshold):
        return False
    if templatefile is None:
        raise ValueError("must have template file for Fluent files")
    template_store = fluent.FluentFile(templatefile)
    output_store = po2fluent(includefuzzy).convert_store(template_store, inputstore)
    output_store.serialize(outputfile)
    return 1


def main(argv=None) -> None:
    formats = {
        ("po", "ftl"): ("ftl", convertfluent),
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
