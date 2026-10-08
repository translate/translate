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

import gettext
import logging
import subprocess
import sys
from io import BytesIO

import pytest
from fluent.syntax import ast, parse

from translate.convert import fluent2po, po2fluent
from translate.misc import cldr_plurals
from translate.storage import fluent, po

from . import test_convert

PLURAL_FORMS = {
    "ja": "nplurals=1; plural=0;",
    "zh": "nplurals=1; plural=0;",
    "en": "nplurals=2; plural=(n != 1);",
    "de": "nplurals=2; plural=(n != 1);",
    "fr": "nplurals=2; plural=(n > 1);",
    "ru": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && "
        "(n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "uk": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && "
        "(n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "pl": (
        "nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && "
        "(n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "cs": "nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;",
    "lt": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && "
        "(n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "ro": "nplurals=3; plural=(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2);",
    "sl": (
        "nplurals=4; plural=(n%100==1 ? 0 : n%100==2 ? 1 : "
        "n%100==3 || n%100==4 ? 2 : 3);"
    ),
    "gd": (
        "nplurals=4; plural=(n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : "
        "(n > 2 && n < 20) ? 2 : 3;"
    ),
    "ar": (
        "nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : "
        "n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5;"
    ),
}

EXPECTED_MAPPINGS = {
    "ja": {"other": 0},
    "zh": {"other": 0},
    "en": {"one": 0, "other": 1},
    "de": {"one": 0, "other": 1},
    # 1000000 is "many" in French, and uses the gettext plural form.
    "fr": {"one": 0, "many": 1, "other": 1},
    # "other" only covers fractions, it reuses "few".
    "ru": {"one": 0, "few": 1, "many": 2, "other": 1},
    "uk": {"one": 0, "few": 1, "many": 2, "other": 1},
    # "other" only covers fractions, it reuses the last form.
    "pl": {"one": 0, "few": 1, "many": 2, "other": 2},
    # "many" only covers fractions, it is left to the default variant.
    "cs": {"one": 0, "few": 1, "other": 2},
    "lt": {"one": 0, "few": 1, "other": 2},
    "ro": {"one": 0, "few": 1, "other": 2},
    "sl": {"one": 0, "two": 1, "few": 2, "other": 3},
    "gd": {"one": 0, "two": 1, "few": 2, "other": 3},
    "ar": {"zero": 0, "one": 1, "two": 2, "few": 3, "many": 4, "other": 5},
}

NUMBERS = (0, 1, 2, 3, 5, 6, 11, 12, 21, 22, 25, 100, 101, 102, 111, 1000000)
CHECKED_NUMBERS = (0, 1, 2, 5, 11, 21, 22, 25, 111)

EMAILS_TEMPLATE = """\
emails =
    { $count ->
        [one] You have one email
       *[other] You have { $count } emails
    }
"""


def po_header(language=None, plural_forms=None) -> str:
    lines = ['msgid ""', 'msgstr ""', '"Content-Type: text/plain; charset=UTF-8\\n"']
    if language is not None:
        lines.append(f'"Language: {language}\\n"')
    if plural_forms is not None:
        lines.append(f'"Plural-Forms: {plural_forms}\\n"')
    return "\n".join(lines) + "\n\n"


def po_quote(text: str) -> str:
    return (
        '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    )


def po_unit(location, source, target, plural=None, flags=None, context=None) -> str:
    lines = []
    if flags:
        lines.append(f"#, {flags}")
    if location:
        lines.append(f"#: {location}")
    if context:
        lines.append(f"msgctxt {po_quote(context)}")
    lines.append(f"msgid {po_quote(source)}")
    if plural is None:
        lines.append(f"msgstr {po_quote(target)}")
    else:
        lines.append(f"msgid_plural {po_quote(plural)}")
        lines.extend(f"msgstr[{i}] {po_quote(text)}" for i, text in enumerate(target))
    return "\n".join(lines) + "\n\n"


def plural_forms_for(language, count=None):
    """Translations of the emails message for every gettext form."""
    count = count or int(PLURAL_FORMS[language].split(";")[0].split("=")[1])
    return [f"{language}{index} {{ $count }}" for index in range(count)]


def convert(posource, template, includefuzzy=False) -> str:
    """Convert PO source into Fluent using a Fluent template."""
    inputstore = po.pofile(BytesIO(posource.encode()))
    templatestore = fluent.FluentFile(BytesIO(template.encode()))
    convertor = po2fluent.po2fluent(includefuzzy=includefuzzy)
    output = BytesIO()
    convertor.convert_store(templatestore, inputstore).serialize(output)
    return output.getvalue().decode()


def canonical(ftl: str) -> str:
    """Re-serialize Fluent source to compare it independently of formatting."""
    output = BytesIO()
    fluent.FluentFile(BytesIO(ftl.encode())).serialize(output)
    return output.getvalue().decode()


def get_entry(ftl, entry_id):
    for entry in parse(ftl).body:
        if isinstance(entry, (ast.Message, ast.Term)):
            name = (
                entry.id.name if isinstance(entry, ast.Message) else f"-{entry.id.name}"
            )
            if name == entry_id:
                return entry
    raise KeyError(entry_id)


def pattern_text(pattern) -> str:
    parts = []
    for element in pattern.elements:
        if isinstance(element, ast.TextElement):
            parts.append(element.value)
        else:
            assert isinstance(element.expression, ast.VariableReference)
            parts.append(f"{{ ${element.expression.id.name} }}")
    return "".join(parts)


def get_select(ftl, entry_id="emails"):
    entry = get_entry(ftl, entry_id)
    assert len(entry.value.elements) == 1
    select = entry.value.elements[0].expression
    assert isinstance(select, ast.SelectExpression)
    return select


def variants(ftl, entry_id="emails") -> dict[str, str]:
    return {
        variant.key.name: pattern_text(variant.value)
        for variant in get_select(ftl, entry_id).variants
    }


def default_variant(ftl, entry_id="emails") -> str:
    (default,) = [v for v in get_select(ftl, entry_id).variants if v.default]
    return default.key.name


def resolve(ftl, language, number, entry_id="emails") -> str:
    """Resolve a plural message like a Fluent runtime would."""
    category = cldr_plurals.get_category(language, number)
    select = get_select(ftl, entry_id)
    for variant in select.variants:
        if variant.key.name == category:
            return pattern_text(variant.value)
    for variant in select.variants:
        if variant.default:
            return pattern_text(variant.value)
    raise AssertionError  # pragma: no cover


def plural_po(language, forms=None, plural_forms=None, header_language=None):
    plural_forms = PLURAL_FORMS[language] if plural_forms is None else plural_forms
    forms = plural_forms_for(language) if forms is None else forms
    return po_header(header_language or language, plural_forms) + po_unit(
        "emails", "You have one email", forms, plural="You have { $count } emails"
    )


class TestPluralMapping:
    @pytest.mark.parametrize(("language", "expected"), EXPECTED_MAPPINGS.items())
    def test_mapping(self, language, expected) -> None:
        nplurals, plural = po2fluent.gettext_plural_forms(PLURAL_FORMS[language])
        mapping = po2fluent.get_plural_mapping(language, nplurals, plural)
        assert mapping == expected
        assert list(mapping) == [c for c in cldr_plurals.CATEGORIES if c in expected], (
            "categories are in CLDR order"
        )

    @pytest.mark.parametrize("language", EXPECTED_MAPPINGS)
    def test_matches_gettext(self, language) -> None:
        """Every integer gets the same text from Fluent as from gettext."""
        nplurals, plural = po2fluent.gettext_plural_forms(PLURAL_FORMS[language])
        expression = gettext.c2py(plural)
        forms = plural_forms_for(language)
        output = convert(plural_po(language), EMAILS_TEMPLATE)
        if nplurals == 1:
            assert "->" not in output
            return
        for number in (*NUMBERS, *range(200)):
            assert resolve(output, language, number) == forms[expression(number)], (
                number
            )

    @pytest.mark.parametrize("language", ["en", "ru", "uk"])
    @pytest.mark.parametrize("number", CHECKED_NUMBERS)
    def test_checked_numbers(self, language, number) -> None:
        forms = ["{ $count } file", "{ $count } files"]
        if language == "ru":
            forms = ["{ $count } файл", "{ $count } файла", "{ $count } файлов"]
        elif language == "uk":
            forms = ["{ $count } файл", "{ $count } файли", "{ $count } файлів"]
        expected = {
            "en": {1: 0},
            "ru": {1: 0, 21: 0, 2: 1, 22: 1},
            "uk": {1: 0, 21: 0, 2: 1, 22: 1},
        }[language].get(number, 1 if language == "en" else 2)
        output = convert(plural_po(language, forms), EMAILS_TEMPLATE)
        assert resolve(output, language, number) == forms[expected]

    @pytest.mark.parametrize("language", ["ru", "uk"])
    def test_fractions_use_few(self, language) -> None:
        forms = ["один", "несколько", "много"]
        output = convert(plural_po(language, forms), EMAILS_TEMPLATE)
        assert default_variant(output) == "other"
        assert resolve(output, language, "1.5") == "несколько"
        assert resolve(output, language, "0.5") == "несколько"

    def test_fractions_polish_use_last_form(self) -> None:
        forms = ["plik", "pliki", "plików"]
        output = convert(plural_po("pl", forms), EMAILS_TEMPLATE)
        assert variants(output)["other"] == "plików"
        assert resolve(output, "pl", "1.5") == "plików"

    def test_fractions_czech_use_default(self) -> None:
        forms = ["soubor", "soubory", "souborů"]
        output = convert(plural_po("cs", forms), EMAILS_TEMPLATE)
        assert "many" not in variants(output)
        assert resolve(output, "cs", "1.5") == "souborů"

    def test_all_categories_in_output(self) -> None:
        output = convert(plural_po("ar"), EMAILS_TEMPLATE)
        assert list(variants(output)) == list(cldr_plurals.CATEGORIES)
        assert default_variant(output) == "other"
        assert output == (
            "emails =\n"
            "    { $count ->\n"
            "        [zero] ar0 { $count }\n"
            "        [one] ar1 { $count }\n"
            "        [two] ar2 { $count }\n"
            "        [few] ar3 { $count }\n"
            "        [many] ar4 { $count }\n"
            "       *[other] ar5 { $count }\n"
            "    }\n"
        )

    def test_uk_output(self) -> None:
        forms = ["{ $count } лист", "{ $count } листи", "{ $count } листів"]
        output = convert(plural_po("uk", forms), EMAILS_TEMPLATE)
        assert output == (
            "emails =\n"
            "    { $count ->\n"
            "        [one] { $count } лист\n"
            "        [few] { $count } листи\n"
            "        [many] { $count } листів\n"
            "       *[other] { $count } листи\n"
            "    }\n"
        )

    @pytest.mark.parametrize("language", ["ja", "zh"])
    def test_single_form(self, language) -> None:
        output = convert(plural_po(language, ["{ $count }件"]), EMAILS_TEMPLATE)
        assert output == "emails = { $count }件\n"

    def test_language_with_region(self) -> None:
        posource = plural_po("uk", header_language="uk_UA")
        assert variants(convert(posource, EMAILS_TEMPLATE))["few"] == "uk1 { $count }"

    def test_portugal(self) -> None:
        """pt-PT has its own CLDR rules: 0 is not "one"."""
        plural_forms = "nplurals=2; plural=(n != 1);"
        mapping = po2fluent.get_plural_mapping("pt_PT", 2, "(n != 1)")
        assert mapping == {"one": 0, "many": 1, "other": 1}
        brazil = po2fluent.get_plural_mapping("pt_BR", 2, "(n > 1)")
        assert brazil == {"one": 0, "many": 1, "other": 1}
        output = convert(
            plural_po("en", plural_forms=plural_forms, header_language="pt_PT"),
            EMAILS_TEMPLATE,
        )
        assert resolve(output, "pt-PT", 0) == "en1 { $count }"

    def test_split_category_warns(self, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            mapping = po2fluent.get_plural_mapping("en", 3, "n==1 ? 0 : n<10 ? 1 : 2")
        assert mapping == {"one": 0, "other": 2}
        assert "split over gettext forms [1, 2]" in caplog.text

    def test_unused_form_warns(self, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            mapping = po2fluent.get_plural_mapping("ja", 2, "(n != 1)")
        assert mapping == {"other": 1}
        assert "forms [0] are not used" in caplog.text

    def test_unknown_language_single_form(self) -> None:
        assert po2fluent.get_plural_mapping("xx", 1, "0") == {"other": 0}
        assert po2fluent.get_plural_mapping(None, 1, "0") == {"other": 0}

    @pytest.mark.parametrize(
        ("language", "nplurals", "plural", "message"),
        [
            ("xx", 2, "(n != 1)", "Unknown CLDR plural rules"),
            (None, 2, "(n != 1)", "Unknown CLDR plural rules"),
            ("en", 2, "n +* 1", "Invalid plural expression"),
            ("en", 0, "0", "Invalid nplurals"),
            ("en", 2, "n", "gives form 2 for 2"),
        ],
    )
    def test_invalid(self, language, nplurals, plural, message) -> None:
        with pytest.raises(po2fluent.PluralFormsError, match=message):
            po2fluent.get_plural_mapping(language, nplurals, plural)


class TestPluralForms:
    def get(self, header):
        return po2fluent.get_plural_forms(po.pofile(BytesIO(header.encode())))

    def test_header(self) -> None:
        assert self.get(po_header("en", "nplurals=2; plural=(n != 1);")) == (
            "en",
            2,
            "(n != 1)",
        )

    def test_missing_header_uses_language_data(self) -> None:
        language, nplurals, plural = self.get(po_header("uk"))
        assert (language, nplurals) == ("uk", 3)
        assert gettext.c2py(plural)(22) == 1

    def test_language_data_base_language(self) -> None:
        assert self.get(po_header("de_AT"))[1:] == (2, "(n != 1)")

    def test_invalid_header_uses_language_data(self, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            result = self.get(po_header("de", "nplurals=2; plural=n +* 1;"))
        assert result == ("de", 2, "(n != 1)")
        assert "Invalid Plural-Forms header" in caplog.text

    def test_non_numeric_nplurals(self, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            result = self.get(po_header("de", "nplurals=two; plural=(n != 1);"))
        assert result == ("de", 2, "(n != 1)")

    def test_unknown(self) -> None:
        assert self.get(po_header("xx")) == ("xx", None, None)
        assert self.get(po_header()) == (None, None, None)
        assert self.get("") == (None, None, None)

    def test_gettext_plural_forms_helper(self) -> None:
        assert po2fluent.gettext_plural_forms("nplurals=1; plural=0;") == (1, "0")


class TestPO2Fluent:
    def test_simple(self) -> None:
        posource = po_unit("hello", "Hello", "Hola")
        assert convert(posource, "hello = Hello\n") == "hello = Hola\n"

    def test_template_structure_kept(self) -> None:
        template = """\
### Resource comment

## Group comment

# Message comment
hello = Hello
# Standalone comment

bye = Bye
"""
        posource = po_unit("hello", "Hello", "Hola") + po_unit("bye", "Bye", "Adéu")
        assert convert(posource, template) == canonical(
            template.replace("= Hello", "= Hola").replace("= Bye", "= Adéu")
        )

    def test_missing_entry_uses_template(self) -> None:
        template = "hello = Hello\nbye = Bye\n"
        posource = po_unit("hello", "Hello", "Hola")
        assert convert(posource, template) == "hello = Hola\nbye = Bye\n"

    def test_empty_translation_uses_template(self) -> None:
        posource = po_unit("hello", "Hello", "")
        assert convert(posource, "hello = Hello\n") == "hello = Hello\n"

    def test_fuzzy(self) -> None:
        posource = po_unit("hello", "Hello", "Hola", flags="fuzzy")
        assert convert(posource, "hello = Hello\n") == "hello = Hello\n"
        assert (
            convert(posource, "hello = Hello\n", includefuzzy=True) == "hello = Hola\n"
        )

    def test_fuzzy_empty(self) -> None:
        posource = po_unit("hello", "Hello", "", flags="fuzzy")
        assert (
            convert(posource, "hello = Hello\n", includefuzzy=True) == "hello = Hello\n"
        )

    def test_obsolete_ignored(self) -> None:
        posource = '#~ msgctxt "hello"\n#~ msgid "Hello"\n#~ msgstr "Hola"\n'
        assert convert(posource, "hello = Hello\n") == "hello = Hello\n"

    def test_msgctxt(self) -> None:
        posource = po_unit(None, "Hello", "Hola", context="hello")
        assert convert(posource, "hello = Hello\n") == "hello = Hola\n"

    def test_location_preferred_over_msgctxt(self) -> None:
        posource = po_unit("hello", "Hello", "Hola", context="other") + po_unit(
            None, "Hello", "Bon dia", context="hello"
        )
        assert convert(posource, "hello = Hello\n") == "hello = Hola\n"

    def test_duplicate_location_first_wins(self) -> None:
        posource = po_unit("hello", "Hello", "Hola") + po_unit(
            "hello", "Hello!", "Bon dia"
        )
        assert convert(posource, "hello = Hello\n") == "hello = Hola\n"

    def test_multiple_locations(self) -> None:
        posource = po_unit("hello hi", "Hello", "Hola")
        assert convert(posource, "hello = Hello\nhi = Hello\n") == (
            "hello = Hola\nhi = Hola\n"
        )

    def test_po_comments_not_copied(self) -> None:
        posource = "# translator comment\n#. extracted comment\n" + po_unit(
            "hello", "Hello", "Hola"
        )
        template = "# Developer comment\nhello = Hello\n"
        assert convert(posource, template) == "# Developer comment\nhello = Hola\n"

    def test_variables(self) -> None:
        posource = po_unit(
            "greeting", "Hello { $name }, { $count }", "Hola { $name }, { $count }"
        )
        output = convert(posource, "greeting = Hello { $name }, { $count }\n")
        assert output == "greeting = Hola { $name }, { $count }\n"

    def test_multiline(self) -> None:
        template = "multi =\n    First line\n    second line\n"
        posource = po_unit(
            "multi", "First line\nsecond line", "Primera\nsegona\n\ntercera"
        )
        assert convert(posource, template) == (
            "multi =\n    Primera\n    segona\n\n    tercera\n"
        )

    def test_attributes(self) -> None:
        template = "login =\n    .placeholder = Email\n    .title = Login\n"
        posource = po_unit(
            "login",
            ".placeholder = Email\n.title = Login",
            ".placeholder = Correu\n.title = Entra",
        )
        assert convert(posource, template) == (
            "login =\n    .placeholder = Correu\n    .title = Entra\n"
        )

    def test_value_and_attributes(self) -> None:
        template = "login = Login\n    .title = Login now\n"
        posource = po_unit(
            "login", "Login\n.title = Login now", "Entra\n.title = Entra ara"
        )
        assert convert(posource, template) == "login = Entra\n    .title = Entra ara\n"

    def test_duplicate_attribute_uses_template(self, caplog) -> None:
        template = "login = Login\n"
        posource = po_unit("login", "Login", "Entra\n.title = A\n.title = B")
        with caplog.at_level(logging.WARNING):
            assert convert(posource, template) == template
        assert "assigned to more than once" in caplog.text

    def test_terms(self) -> None:
        template = (
            "-brand = Firefox\n    .gender = masculine\nabout = About { -brand }\n"
        )
        posource = po_unit(
            "-brand", "Firefox\n.gender = masculine", "Firefox\n.gender = feminine"
        ) + po_unit("about", "About { -brand }", "Quant a { -brand }")
        assert convert(posource, template) == (
            "-brand = Firefox\n    .gender = feminine\nabout = Quant a { -brand }\n"
        )

    def test_term_without_value_uses_template(self, caplog) -> None:
        template = "-brand = Firefox\n"
        posource = po_unit("-brand", "Firefox", ".gender = masculine")
        with caplog.at_level(logging.WARNING):
            assert convert(posource, template) == template
        assert "-brand" in caplog.text

    def test_select_in_singular(self) -> None:
        """fluent2po keeps select expressions as Fluent syntax."""
        translation = (
            "{ $count ->\n    [one] Un correu\n   *[other] { $count } correus\n}"
        )
        posource = po_unit("emails", "ignored", translation)
        assert variants(convert(posource, EMAILS_TEMPLATE)) == {
            "one": "Un correu",
            "other": "{ $count } correus",
        }

    def test_select_on_gender(self) -> None:
        template = "shared = { $gender ->\n   *[other] Shared\n}\n"
        translation = "{ $gender ->\n    [female] Compartida\n   *[other] Compartit\n}"
        posource = po_unit("shared", "ignored", translation)
        output = convert(posource, template)
        assert variants(output, "shared") == {
            "female": "Compartida",
            "other": "Compartit",
        }

    def test_mixed_plural_and_singular(self) -> None:
        template = (
            "title = Mail\n"
            + EMAILS_TEMPLATE
            + "unread = { $count } unread\nbye = Bye\n"
        )
        posource = (
            po_header("uk", PLURAL_FORMS["uk"])
            + po_unit("title", "Mail", "Пошта")
            + po_unit(
                "emails",
                "You have one email",
                ["{ $count } лист", "{ $count } листи", "{ $count } листів"],
                plural="You have { $count } emails",
            )
            + po_unit(
                "unread",
                "{ $count } unread",
                [
                    "{ $count } непрочитаний",
                    "{ $count } непрочитані",
                    "{ $count } непрочитаних",
                ],
                plural="{ $count } unread",
            )
        )
        output = convert(posource, template)
        assert get_entry(output, "title").value.elements[0].value == "Пошта"
        assert variants(output)["few"] == "{ $count } листи"
        assert variants(output, "unread")["many"] == "{ $count } непрочитаних"
        assert "bye = Bye\n" in output

    def test_plural_attributes_from_template(self) -> None:
        template = EMAILS_TEMPLATE + "    .title = Inbox\n"
        output = convert(plural_po("en"), template)
        entry = get_entry(output, "emails")
        assert [a.id.name for a in entry.attributes] == ["title"]
        assert variants(output) == {"one": "en0 { $count }", "other": "en1 { $count }"}

    def test_plural_term(self) -> None:
        template = "-apples = { $count ->\n    [one] apple\n   *[other] apples\n}\n"
        posource = po_header("en", PLURAL_FORMS["en"]) + po_unit(
            "-apples", "apple", ["poma", "pomes"], plural="apples"
        )
        output = convert(posource, template)
        assert output.startswith("-apples =\n    { $count ->\n")
        assert variants(output, "-apples") == {"one": "poma", "other": "pomes"}

    def test_plural_selector_from_template(self) -> None:
        template = (
            "emails = { NUMBER($total, minimumFractionDigits: 0) ->\n"
            "    [0] None\n   *[other] Some\n}\n"
        )
        output = convert(plural_po("en"), template)
        assert "{ NUMBER($total, minimumFractionDigits: 0) ->" in output

    def test_plural_selector_ignores_non_plural_select(self) -> None:
        template = "emails = { $gender ->\n   *[male] { $n } emails\n}\n"
        posource = po_header("en", PLURAL_FORMS["en"]) + po_unit(
            "emails",
            "{ $n } email",
            ["{ $n } correu", "{ $n } correus"],
            plural="{ $n } emails",
        )
        assert "{ $n ->" in convert(posource, template)

    def test_plural_selector_after_text(self) -> None:
        template = "emails = Total: { $total } { $n ->\n    [one] email\n   *[other] emails\n}\n"
        output = convert(plural_po("en"), template)
        assert "{ $n ->" in output

    def test_plural_attribute_only_template(self) -> None:
        template = "emails =\n    .title = Emails\n"
        output = convert(plural_po("en"), template)
        assert variants(output) == {"one": "en0 { $count }", "other": "en1 { $count }"}
        assert "    .title = Emails\n" in output

    def test_plural_selector_from_strings(self) -> None:
        posource = po_header("en", PLURAL_FORMS["en"]) + po_unit(
            "files",
            "One file",
            ["Un fitxer", "{ $num } fitxers"],
            plural="Many files",
        )
        assert "{ $num ->" in convert(posource, "files = Files\n")

    def test_plural_selector_default(self) -> None:
        posource = po_header("en", PLURAL_FORMS["en"]) + po_unit(
            "files", "One file", ["Un fitxer", "Fitxers"], plural="Files"
        )
        assert "{ $count ->" in convert(posource, "files = Files\n")

    def test_plural_empty_form_uses_template(self) -> None:
        posource = plural_po("uk", ["один", "", "багато"])
        assert convert(posource, EMAILS_TEMPLATE) == EMAILS_TEMPLATE

    def test_plural_fuzzy(self) -> None:
        posource = po_header("en", PLURAL_FORMS["en"]) + po_unit(
            "emails", "One", ["Un", "Molts"], plural="Many", flags="fuzzy"
        )
        assert convert(posource, EMAILS_TEMPLATE) == EMAILS_TEMPLATE
        output = convert(posource, EMAILS_TEMPLATE, includefuzzy=True)
        assert variants(output) == {"one": "Un", "other": "Molts"}

    def test_plural_multiline(self) -> None:
        posource = plural_po("en", ["Un\ncorreu", "Molts\ncorreus"])
        output = convert(posource, EMAILS_TEMPLATE)
        assert output == (
            "emails =\n"
            "    { $count ->\n"
            "        [one]\n"
            "            Un\n"
            "            correu\n"
            "       *[other]\n"
            "            Molts\n"
            "            correus\n"
            "    }\n"
        )

    def test_plural_escaped(self) -> None:
        forms = ['{"["}un{"]"} {"{"}', '{"*"}molts{"."} {"}"}']
        output = convert(plural_po("en", forms), EMAILS_TEMPLATE)
        assert '[one] { "[" }un{ "]" } { "{" }' in output
        assert '*[other] { "*" }molts{ "." } { "}" }' in output
        assert canonical(output) == output

    @pytest.mark.parametrize(
        "form",
        ["un { correu", "un\n.title = attribute", "un\n*[other] x", "{ $count ->"],
    )
    def test_plural_invalid_form_uses_template(self, form, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            output = convert(plural_po("en", [form, "molts"]), EMAILS_TEMPLATE)
        assert output == EMAILS_TEMPLATE
        assert "Using the template for emails" in caplog.text

    def test_plural_whitespace_only_form_uses_template(self, caplog) -> None:
        with caplog.at_level(logging.WARNING):
            output = convert(plural_po("en", ["  ", "molts"]), EMAILS_TEMPLATE)
        assert output == EMAILS_TEMPLATE
        assert "Using the template for emails" in caplog.text


class TestEscaping:
    @pytest.mark.parametrize(
        ("translation", "expected"),
        [
            ('Fes servir {"{"} i {"}"}', 'msg = Fes servir { "{" } i { "}" }\n'),
            ('Fes servir { "{" }', 'msg = Fes servir { "{" }\n'),
            ('{"["}obert{"]"}', 'msg = { "[" }obert{ "]" }\n'),
            ("text [not a variant] * .", "msg = text [not a variant] * .\n"),
            ('{"  "}espais', 'msg = { "  " }espais\n'),
            ('espais{"  "}', 'msg = espais{ "  " }\n'),
            ('{"*"} estrella', 'msg = { "*" } estrella\n'),
            (
                'línia\n{"."}punt\n{"*"}estrella\n{"["}claudàtor',
                (
                    'msg =\n    línia\n    { "." }punt\n    { "*" }estrella\n'
                    '    { "[" }claudàtor\n'
                ),
            ),
            ('Cometes "altes" i {"\\""}', 'msg = Cometes "altes" i { "\\"" }\n'),
            ('Unicode {"\\u00A0"}', 'msg = Unicode { "\\u00A0" }\n'),
            ("  espais al voltant  ", "msg = espais al voltant\n"),
        ],
    )
    def test_valid(self, translation, expected) -> None:
        posource = po_unit("msg", "Message", translation)
        assert convert(posource, "msg = Message\n") == expected

    @pytest.mark.parametrize(
        "translation",
        [
            "obert { sense tancar",
            "tancat } sense obrir",
            "línia\n*[other] variant",
            "línia\n[one] variant",
            "{ $count ->\n   [one] sense defecte\n}",
            '{ "sense tancar }',
        ],
    )
    def test_invalid_uses_template(self, translation, caplog) -> None:
        posource = po_unit("msg", "Message", translation)
        with caplog.at_level(logging.WARNING):
            assert convert(posource, "msg = Message\n") == "msg = Message\n"
        assert "Using the template for msg" in caplog.text

    def test_leading_dot_is_attribute(self) -> None:
        """A line starting with a dot starts an attribute, as in fluent2po."""
        posource = po_unit("msg", "Message", "Valor\n.title = Títol")
        assert (
            convert(posource, "msg = Message\n") == "msg = Valor\n    .title = Títol\n"
        )


class TestEdgeCases:
    TEMPLATE = "hello = Hello\n" + EMAILS_TEMPLATE

    def test_empty_po(self) -> None:
        assert convert("", self.TEMPLATE) == self.TEMPLATE

    def test_header_only_po(self) -> None:
        posource = po_header("uk", PLURAL_FORMS["uk"])
        assert convert(posource, self.TEMPLATE) == self.TEMPLATE

    def test_empty_template(self) -> None:
        assert convert(po_unit("hello", "Hello", "Hola"), "") == ""

    def test_missing_plural_forms_uses_language_data(self) -> None:
        posource = plural_po("uk", plural_forms="")
        posource = posource.replace('"Plural-Forms: \\n"\n', "")
        assert "Plural-Forms" not in posource
        assert variants(convert(posource, EMAILS_TEMPLATE))["many"] == "uk2 { $count }"

    def test_missing_plural_forms_and_language(self, caplog) -> None:
        posource = po_unit("emails", "One", ["Un", "Molts"], plural="Many") + po_unit(
            "hello", "Hello", "Hola"
        )
        with caplog.at_level(logging.WARNING):
            output = convert(posource, self.TEMPLATE)
        assert output == self.TEMPLATE.replace("= Hello", "= Hola")
        assert "please set the Plural-Forms header" in caplog.text

    def test_invalid_plural_forms_unknown_language(self, caplog) -> None:
        posource = plural_po(
            "en",
            ["Un", "Molts"],
            plural_forms="nplurals=2; plural=n +* 1;",
            header_language="xx",
        )
        with caplog.at_level(logging.WARNING):
            assert convert(posource, EMAILS_TEMPLATE) == EMAILS_TEMPLATE
        assert "Invalid Plural-Forms header" in caplog.text

    def test_plural_forms_out_of_range(self, caplog) -> None:
        posource = plural_po(
            "en", ["Un", "Molts"], plural_forms="nplurals=2; plural=n;"
        )
        with caplog.at_level(logging.WARNING):
            assert convert(posource, EMAILS_TEMPLATE) == EMAILS_TEMPLATE
        assert "gives form 2" in caplog.text

    def test_unknown_language(self, caplog) -> None:
        posource = plural_po("en", header_language="xx")
        with caplog.at_level(logging.WARNING):
            assert convert(posource, EMAILS_TEMPLATE) == EMAILS_TEMPLATE
        assert "Unknown CLDR plural rules for language 'xx'" in caplog.text

    def test_unknown_language_single_form(self) -> None:
        posource = plural_po("ja", ["{ $count }"], header_language="xx")
        assert convert(posource, EMAILS_TEMPLATE) == "emails = { $count }\n"

    def test_fewer_forms_than_nplurals(self, caplog) -> None:
        posource = plural_po("uk", ["один", "два"])
        with caplog.at_level(logging.WARNING):
            assert convert(posource, EMAILS_TEMPLATE) == EMAILS_TEMPLATE
        assert "Found 2 plural forms, but nplurals=3" in caplog.text

    def test_more_forms_than_nplurals(self, caplog) -> None:
        posource = plural_po("en", ["un", "molts", "massa"])
        with caplog.at_level(logging.WARNING):
            output = convert(posource, EMAILS_TEMPLATE)
        assert variants(output) == {"one": "un", "other": "molts"}
        assert "Ignoring 1 extra plural forms of emails" in caplog.text

    def test_plural_with_gettext_nplurals_mismatch_language(self, caplog) -> None:
        """Header says 2 forms while Ukrainian has 3 CLDR integer categories."""
        posource = plural_po("uk", ["один", "багато"], plural_forms=PLURAL_FORMS["en"])
        with caplog.at_level(logging.WARNING):
            output = convert(posource, EMAILS_TEMPLATE)
        assert variants(output) == {
            "one": "багато",
            "few": "багато",
            "many": "багато",
            "other": "багато",
        }
        assert "split over gettext forms" in caplog.text


class TestRoundTrip:
    TEMPLATE = """\
### Resource comment

## Group

# Shown in the inbox
emails =
    { $count ->
        [one] You have one email
       *[other] You have { $count } emails
    }
    .title = Inbox
multi =
    First line
    second line
braces = Use { "{" } and { "}" }
lead = { "  " }spaces
-brand = Firefox
    .gender = masculine
about = About { -brand }
attrs =
    .label = Label
untranslated = Untranslated
"""
    TRANSLATION = """\
### Resource comment

## Group

# Shown in the inbox
emails = { $count ->
    [one] Tens un correu
   *[other] Tens { $count } correus
}
    .title = Safata
multi =
    Primera línia
    segona línia
braces = Fes servir {"{"} i {"}"}
lead = {"  "}espais
-brand = Firefox
    .gender = masculine
about = Quant a { -brand }
attrs =
    .label = Etiqueta
"""

    def test_roundtrip(self) -> None:
        template = fluent.FluentFile(BytesIO(self.TEMPLATE.encode()))
        translation = fluent.FluentFile(BytesIO(self.TRANSLATION.encode()))
        postore = fluent2po.fluent2po().merge_store(template, translation)
        output = convert(bytes(postore).decode(), self.TEMPLATE)
        assert output == canonical(self.TRANSLATION) + "untranslated = Untranslated\n"

    def test_roundtrip_unchanged_template(self) -> None:
        template = fluent.FluentFile(BytesIO(self.TEMPLATE.encode()))
        postore = fluent2po.fluent2po().convert_store(template)
        output = convert(bytes(postore).decode(), self.TEMPLATE)
        assert output == canonical(self.TEMPLATE)


class TestConvertFunction:
    def test_convertfluent(self) -> None:
        output = BytesIO()
        result = po2fluent.convertfluent(
            BytesIO(po_unit("hello", "Hello", "Hola").encode()),
            output,
            BytesIO(b"hello = Hello\n"),
        )
        assert result == 1
        assert output.getvalue() == b"hello = Hola\n"

    def test_convertfluent_fuzzy(self) -> None:
        output = BytesIO()
        po2fluent.convertfluent(
            BytesIO(po_unit("hello", "Hello", "Hola", flags="fuzzy").encode()),
            output,
            BytesIO(b"hello = Hello\n"),
            includefuzzy=True,
        )
        assert output.getvalue() == b"hello = Hola\n"

    def test_no_template(self) -> None:
        with pytest.raises(ValueError, match="must have template file"):
            po2fluent.convertfluent(BytesIO(b""), BytesIO(), None)

    def test_threshold(self) -> None:
        posource = po_unit("hello", "Hello", "Hola") + po_unit("bye", "Bye", "")
        output = BytesIO()
        result = po2fluent.convertfluent(
            BytesIO(posource.encode()),
            output,
            BytesIO(b"hello = Hello\nbye = Bye\n"),
            outputthreshold=80,
        )
        assert not result
        assert output.getvalue() == b""


class TestPO2FluentCommand(test_convert.TestConvertCommand):
    """Tests running actual po2fluent commands on files."""

    convertmodule = po2fluent
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]

    def test_convert(self) -> None:
        self.create_testfile("template.ftl", EMAILS_TEMPLATE + "hello = Hello\n")
        self.create_testfile(
            "uk.po",
            plural_po(
                "uk", ["{ $count } лист", "{ $count } листи", "{ $count } листів"]
            )
            + po_unit("hello", "Hello", "Привіт", flags="fuzzy"),
        )
        self.run_command("-t", "template.ftl", "uk.po", "uk.ftl")
        output = self.read_testfile("uk.ftl").decode()
        assert variants(output)["many"] == "{ $count } листів"
        assert "hello = Hello\n" in output
        self.run_command("-t", "template.ftl", "uk.po", "uk-fuzzy.ftl", fuzzy=True)
        assert "hello = Привіт\n" in self.read_testfile("uk-fuzzy.ftl").decode()

    def test_run_as_module(self, tmp_path) -> None:
        (tmp_path / "template.ftl").write_text("hello = Hello\n", encoding="utf-8")
        (tmp_path / "ca.po").write_text(
            po_unit("hello", "Hello", "Hola"), encoding="utf-8"
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "translate.convert.po2fluent",
                "--progress=none",
                "-t",
                "template.ftl",
                "ca.po",
                "ca.ftl",
            ],
            cwd=tmp_path,
            check=True,
        )
        assert (tmp_path / "ca.ftl").read_bytes() == b"hello = Hola\n"

    def test_convert_directory(self) -> None:
        self.create_testfile("templates/app.ftl", "hello = Hello\n")
        self.create_testfile("po/app.po", po_unit("hello", "Hello", "Hola"))
        self.run_command("-t", "templates", "po", "ca")
        assert self.read_testfile("ca/app.ftl") == b"hello = Hola\n"
