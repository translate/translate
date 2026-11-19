import os
import plistlib
import re

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import base

PLURAL_REFERENCE_RE = re.compile(r"%(?:\d+\$)?#@(?P<variable>[^@]+)@")


class StringsDictId(base.UnitId):
    KEY_SEPARATOR = ":"

    def __str__(self) -> str:
        s = super().__str__()
        if s.startswith(":"):
            return s[1:]
        return s


class StringsDictUnit(base.NamedPluralUnit, base.DictUnit):
    """
    A single entry in a .stringsdict file.

    Simple plural entries are represented by their plural variable, with the
    localized format string stored as metadata. More complex entries use one
    unit for the localized format string and one unit for each plural variable.
    """

    IdClass = StringsDictId
    format_value_type = ""

    def __init__(self, source=None) -> None:
        super().__init__(source=source)
        self.format_value_type = ""
        self.localized_format: str | None = None

        loc = source or ""
        if len(loc) > 0 and loc[0] == ":":
            loc = loc[1:]

        # Check if this unit is a format string or a variable
        split = loc.rfind(":")
        if split > 0:
            subkey = loc[(split + 1) :]
            loc = loc[:split]
            self.set_unitid(self.IdClass([("key", loc), ("key", subkey)]))
        else:
            self.set_unitid(self.IdClass([("key", loc)]))

    _allows_empty_plural_group = True
    _variable_fields: dict | None = None
    _has_named_edits = False
    _parsed_format_only = False

    _tags_for_locale = staticmethod(data.get_apple_plural_tags)

    def _replace_plural_forms(self, forms: dict[str, str]) -> None:
        if any(tag not in data.cldr_plural_categories for tag in forms):
            raise ValueError("Unknown stringsdict plural category")
        self.set_plural_projection(forms, self._projection)
        self._has_named_edits = True

    def _plural_forms_for_merge(self):
        forms = self.plural_forms
        if (
            forms is not None
            and self._variable_fields is None
            and not self._has_named_edits
        ):
            return self.serialized_forms()
        return forms

    def variable_fields(self) -> dict:
        """Return the variable metadata as it will appear in the plist."""
        plurals = dict(self._variable_fields or {})
        plurals["NSStringFormatSpecTypeKey"] = "NSStringPluralRuleType"
        if self.format_value_type or "NSStringFormatValueTypeKey" in plurals:
            plurals["NSStringFormatValueTypeKey"] = self.format_value_type
        return plurals

    def serialized_forms(self) -> dict:
        """Return explicit categories or apply the legacy positional fallback."""
        if self.innerkey is None:
            return {}
        if self._variable_fields is not None or self._has_named_edits:
            forms = self.plural_forms
            if forms is not None:
                return dict(forms)
        plural_tags = (
            self._store._get_target_plural_tags(self.target)
            if self._store is not None
            else list(self._projection)
        )
        if not plural_tags:
            return {}
        plural_strings = self.sync_plural_count(self.target, plural_tags)
        plurals = {
            plural_tag: plural_string
            for plural_tag, plural_string in zip(
                plural_tags, plural_strings, strict=True
            )
            if plural_string
        }
        # Apple requires "other" even for languages whose represented integer
        # categories end in "many". Keep the existing plural indexes and use
        # the final category as a compatibility fallback.
        if "other" not in plural_tags and plural_strings[-1]:
            plurals["other"] = plural_strings[-1]
        return plurals

    def __eq__(self, other):
        return (
            isinstance(other, StringsDictUnit)
            and super().__eq__(other)
            and self.localized_format == other.localized_format
            and self.serialized_forms() == other.serialized_forms()
            and self.variable_fields() == other.variable_fields()
        )

    @property
    def outerkey(self):
        unitid = self.get_unitid()

        if len(unitid.parts) < 1:
            return None

        return unitid.parts[0][1]

    @property
    def innerkey(self):
        unitid = self.get_unitid()

        if len(unitid.parts) < 2:
            return None

        return unitid.parts[1][1]

    def getid(self):
        return self.source

    def setid(self, value, unitid=None) -> None:
        self._invalidate_store_indexes()
        previous_innerkey = (
            self.innerkey if getattr(self, "_unitid", None) is not None else None
        )
        self.source = value
        super().setid(value, unitid)
        if self.innerkey is not None and self.innerkey != previous_innerkey:
            self.localized_format = f"%#@{self.innerkey}@"


class StringsDictFile(base.DictStore):
    """
    Class representing a .stringsdict file.

    One entry in a .stringsdict file consists of a format string, and any
    number of variables with plural strings.

    Entries containing a single plural variable referenced directly by the
    localized format string are exposed as one plural unit. Entries with
    literal format text or multiple variables are split into a format-string
    unit and one plural unit per variable.
    """

    UnitClass = StringsDictUnit
    Name = "iOS Stringsdict"
    Mimetypes = ["application/x-plist"]
    Extensions = ["stringsdict"]

    def __init__(self, inputfile=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parse(inputfile)

    def gettargetlanguage(self):
        target_lang = super().gettargetlanguage()

        # If targetlanguage isn't set, we try to extract it from the filename path (if any).
        if target_lang is None and hasattr(self, "filename") and self.filename:
            parent_dir = os.path.split(os.path.dirname(self.filename))[1]
            match = re.search(r"^(\w*).lproj", parent_dir)
            if match is not None:
                target_lang = match.group(1)
                if target_lang.lower() == "base":
                    target_lang = "en"
            else:
                target_lang = self.sourcelanguage

            # Cache it
            self.settargetlanguage(target_lang)

        return target_lang

    def addunit(self, unit) -> None:
        if isinstance(unit, StringsDictUnit) and unit.innerkey is not None:
            unit.bind_plural_projection(self)
        super().addunit(unit)

    def _get_target_plural_tags(self, target=None):
        """
        Get all supported plural tags for the target language.
        Note that 'zero' is supported when there is room for optional forms.
        """
        locale = (
            self.get_base_locale_code()
            if self.gettargetlanguage() is not None
            else None
        )
        count = (
            len(self.UnitClass.get_plural_strings(target))
            if target is not None
            else None
        )
        return data.get_apple_plural_tags(locale, count)

    @property
    def target_plural_tags(self):
        return self._get_target_plural_tags()

    def parse(self, input) -> None:  # ty:ignore[lost-keyword-for-regular-parameter]
        """Read a .stringsdict file into a dictionary, and convert it to translation units."""
        if isinstance(input, (bytes, str)):
            plist = plistlib.loads(input)
        elif input is not None:
            plist = plistlib.load(input)
        else:
            plist = {}

        for key, outer in plist.items():
            if not isinstance(outer, dict):
                raise TypeError(f"{key} is not a dict")

            localized_format = outer.get("NSStringLocalizedFormatKey")
            plural_values = []
            for innerkey, value in outer.items():
                if innerkey == "NSStringLocalizedFormatKey":
                    continue
                if not isinstance(value, dict):
                    raise TypeError(f"Unexpected key {innerkey} in {key}")

                spec_type = value.get("NSStringFormatSpecTypeKey", "")
                if spec_type and spec_type != "NSStringPluralRuleType":
                    raise ValueError(
                        f"{innerkey} in {key} is not of NSStringPluralRuleType"
                    )
                plural_values.append((innerkey, value))

            reference_match = (
                PLURAL_REFERENCE_RE.fullmatch(localized_format)
                if isinstance(localized_format, str)
                else None
            )
            referenced_variable = (
                reference_match.group("variable") if reference_match else None
            )

            # Fold the common one-variable representation into one plural unit.
            # A pure format-only entry still identifies its plural variable and
            # is handled below as an untranslated folded unit.
            if len(plural_values) == 1 and referenced_variable == plural_values[0][0]:
                innerkey, value = plural_values[0]
                self._add_plural_unit(
                    key,
                    innerkey,
                    value,
                    localized_format=localized_format,
                )
                continue

            if not plural_values and referenced_variable is not None:
                self._add_plural_unit(
                    key,
                    referenced_variable,
                    None,
                    localized_format=localized_format,
                )
                continue

            if localized_format is not None:
                u = self.UnitClass()
                u.set_unitid(u.IdClass([("key", key)]))
                u.target = str(localized_format)
                self.addunit(u)

            for innerkey, value in plural_values:
                self._add_plural_unit(key, innerkey, value)

    def _add_plural_unit(
        self,
        outerkey: str,
        innerkey: str,
        value: dict | None,
        *,
        localized_format: str | None = None,
    ) -> None:
        plural_tags = self.target_plural_tags
        unit = self.UnitClass()
        unit.set_unitid(unit.IdClass([("key", outerkey), ("key", innerkey)]))
        fields = value or {}
        forms = {
            tag: text
            for tag, text in fields.items()
            if tag in data.cldr_plural_categories
        }
        if not all(isinstance(text, str) for text in forms.values()):
            raise TypeError("Plural variable values must be strings")
        unit.set_plural_projection(forms, plural_tags)
        if value is not None:
            unit._variable_fields = {
                tag: text for tag, text in fields.items() if tag not in forms
            }
        unit._parsed_format_only = value is None
        unit.format_value_type = fields.get("NSStringFormatValueTypeKey", "")
        unit.localized_format = localized_format
        self.addunit(unit)

    def _serialize_plural(self, unit: StringsDictUnit) -> dict:
        return {**unit.variable_fields(), **unit.serialized_forms()}

    def serialize(self, out) -> None:
        plist = {}

        grouped_units = {}
        for unit in self.units:
            grouped_units.setdefault(unit.outerkey, []).append(unit)

        for outerkey, units in grouped_units.items():
            format_units = [unit for unit in units if unit.innerkey is None]
            plural_units = [unit for unit in units if unit.innerkey is not None]

            # A newly created one-variable plural uses the same folded form as
            # parsed entries. Its ID supplies the variable name and therefore
            # the canonical localized format string.
            if (
                len(plural_units) == 1
                and not format_units
                and plural_units[0].localized_format is not None
            ):
                unit = plural_units[0]
                plurals = self._serialize_plural(unit)

                # Omit an untranslated or incomplete entry instead of writing
                # a dictionary which Apple cannot resolve at runtime.
                if unit._variable_fields is None and "other" not in plurals:
                    if (
                        unit._parsed_format_only
                        and unit._forms == {}
                        and unit.localized_format
                    ):
                        plist[outerkey] = {
                            "NSStringLocalizedFormatKey": unit.localized_format
                        }
                    continue

                plist[outerkey] = {
                    "NSStringLocalizedFormatKey": unit.localized_format
                    or f"%#@{unit.innerkey}@",
                    unit.innerkey: plurals,
                }
                continue

            # A plural-only parsed group may depend on a missing complex format
            # sibling. Its original format cannot be reconstructed safely.
            if (
                plural_units
                and not format_units
                and all(
                    unit._variable_fields is None and not unit._has_named_edits
                    for unit in plural_units
                )
            ):
                continue

            output = {}
            for unit in units:
                if unit.innerkey is None:
                    if isinstance(unit.target, multistring):
                        raise TypeError(
                            "Plural stringsdict unit IDs must include a variable name"
                        )
                    output["NSStringLocalizedFormatKey"] = unit.target or unit.source
                else:
                    output[unit.innerkey] = self._serialize_plural(unit)
            plist[outerkey] = output

        out.write(plistlib.dumps(plist, sort_keys=False))
