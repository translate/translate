#
# Copyright 2025 Translate Toolkit contributors
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Module for handling Apple's XLIFF variant with plural support.

Apple has a custom way of encoding .stringsdict plurals in XLIFF format.
This module provides support for reading and writing this format.

The format uses trans-unit IDs like:
- "key" - the main format string
- "key:variable:dict" - marker for a plural variable (source: NSStringPluralRuleType)
- "key:variable:dict/:string" - format value type (e.g., "d")
- "key:variable:dict/PLURAL_FORM:dict/:string" - plural form strings (e.g., "one", "other")

Plural groups are folded into a single unit with a ``multistring`` source/target,
compatible with how other formats (e.g. .stringsdict) handle plurals.

Reference: https://docs.lokalise.com/en/articles/1400816-xliff-xlf-xliff#plural-support
"""

import os
import re

from lxml import etree

from translate.lang import data
from translate.misc.multistring import multistring
from translate.misc.xml_helpers import getText, setXMLspace
from translate.storage import base, xliff


class AppleStringsXliffUnit(xliff.Xliff1Unit):
    """
    A translation unit in an Apple XLIFF file.

    Regular (non-plural) units behave identically to :class:`xliff.Xliff1Unit`.

    Plural units expose their source/target as :class:`~translate.misc.multistring.multistring`
    objects whose strings list corresponds to the target language's plural forms
    (always including "zero" as the first entry, per Apple convention).
    """

    format_value_type = ""

    def __init__(self, source, **kwargs):
        # Initialise plural attributes BEFORE super().__init__() so that
        # self.source = source (called inside super().__init__) can set them.
        self.format_value_type = ""
        self._plural_source = None
        self._plural_target = None
        self._plural_base_key = None
        self._plural_dirty = False
        super().__init__(source, **kwargs)

    # ------------------------------------------------------------------
    # source / target properties – delegate to XML for regular units,
    # return / store multistring for plural units
    # ------------------------------------------------------------------

    @property
    def source(self):
        if self._plural_source is not None:
            return self._plural_source
        return super().source

    @source.setter
    def source(self, value):
        if isinstance(value, multistring):
            self._plural_source = value
            self._plural_dirty = True
        else:
            self._plural_source = None
            self.setsource(value)

    @property
    def target(self):
        if self._plural_target is not None:
            return self._plural_target
        return super().target

    @target.setter
    def target(self, value):
        if isinstance(value, multistring):
            self._plural_target = value
            self._plural_dirty = True
        else:
            self._plural_target = None
            self.settarget(value)

    def hasplural(self):
        """Return True if this unit represents a plural group."""
        return self._plural_source is not None or self._plural_target is not None

    @property
    def rich_source(self):
        if self._plural_source is not None:
            return base.TranslationUnit.multistring_to_rich(self, self._plural_source)
        return super().rich_source

    @rich_source.setter
    def rich_source(self, value) -> None:
        if self.hasplural():
            self._plural_source = self.rich_to_multistring(value)
            self._plural_dirty = True
        else:
            self.set_rich_source(value)

    @property
    def rich_target(self):
        if self._plural_target is not None:
            return base.TranslationUnit.multistring_to_rich(self, self._plural_target)
        return super().rich_target

    @rich_target.setter
    def rich_target(self, value) -> None:
        if self.hasplural():
            self._plural_target = self.rich_to_multistring(value)
            self._plural_dirty = True
        else:
            self.set_rich_target(value)

    # getid() adds filename prefix then the raw XML id.  For plural units we
    # return the base key (without the ":dict" suffix used in the XML).
    def getid(self):
        if self._plural_base_key is not None:
            uid = ""
            try:
                filename = next(
                    self.xmlelement.iterancestors(self.namespaced("file"))
                ).get("original")
                if filename:
                    uid = filename + xliff.ID_SEPARATOR
            except StopIteration:
                pass
            return uid + self._plural_base_key
        return super().getid()

    # ------------------------------------------------------------------
    # Helpers used during parsing to identify the role of a raw unit
    # ------------------------------------------------------------------

    @property
    def is_plural_marker(self):
        """True if the XML source contains NSStringPluralRuleType."""
        # Read from the XML element directly so the check works before folding
        source_node = self.get_source_dom()
        if source_node is None:
            return False
        raw_src = getText(
            source_node, getattr(self, "_default_xml_space", "preserve")
        )
        return raw_src == "NSStringPluralRuleType"

    @property
    def is_format_type(self):
        """True if this unit specifies a plural format value type (e.g. "d")."""
        unit_id = self.xmlelement.get("id", "")
        return unit_id.endswith(":dict/:string") and not any(
            f"/{tag}:dict/:string" in unit_id for tag in data.cldr_plural_categories
        )

    @property
    def is_plural_form(self):
        """True if this unit contains a plural form string."""
        unit_id = self.xmlelement.get("id", "")
        return any(
            f"/{tag}:dict/:string" in unit_id for tag in data.cldr_plural_categories
        )

    def get_base_key(self):
        """
        Extract the base key from a plural-related XML id.

        Example: "shopping-list:apple:dict/one:dict/:string" -> "shopping-list:apple"
        """
        unit_id = self.xmlelement.get("id", "")
        match = re.match(r"^([^:]+:[^:]+):dict", unit_id)
        if match:
            return match.group(1)
        if ":dict" not in unit_id:
            return unit_id
        return None

    def get_plural_form(self):
        """
        Extract the plural form name from the XML id.

        Example: "shopping-list:apple:dict/one:dict/:string" -> "one"
        """
        unit_id = self.xmlelement.get("id", "")
        for tag in data.cldr_plural_categories:
            if f"/{tag}:dict/:string" in unit_id:
                return tag
        return None


class AppleStringsXliffFile(xliff.Xliff1File):
    """
    An Apple XLIFF file with support for plural strings.

    After parsing, each plural group is represented as a single
    :class:`AppleStringsXliffUnit` whose ``source`` and ``target`` are
    :class:`~translate.misc.multistring.multistring` objects.  The strings
    list corresponds to the plural tags returned by :meth:`target_plural_tags`
    (always starting with "zero").

    :meth:`serialize` expands these merged units back to the Apple XLIFF
    wire format (marker + format-type + per-form trans-units).
    """

    UnitClass = AppleStringsXliffUnit
    Name = "Apple XLIFF"
    Mimetypes = ["application/x-xliff+xml"]
    Extensions = ["xliff", "xlf"]

    def gettargetlanguage(self):
        target_lang = super().gettargetlanguage()

        # If targetlanguage isn't set, try to extract from filename (like stringsdict)
        if target_lang is None and hasattr(self, "filename") and self.filename:
            parent_dir = os.path.split(os.path.dirname(self.filename))[1]
            match = re.search(r"^(\w*).lproj", parent_dir)
            if match is not None:
                target_lang = match.group(1)
                if target_lang.lower() == "base":
                    target_lang = "en"

            # Cache it
            if target_lang:
                self.settargetlanguage(target_lang)

        return target_lang

    @property
    def target_plural_tags(self):
        """
        Return the plural tags for the target language.

        "zero" is always included first (Apple convention).
        """
        target_lang = self.gettargetlanguage()
        if target_lang is None:
            return data.cldr_plural_categories

        tags = self.get_plural_tags().copy()
        if "zero" not in tags:
            tags.insert(0, "zero")
        return tags

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _group_plural_units(self):
        """
        Scan *raw* units (as produced by the parent parser) and group them.

        Returns a dict:
          base_key -> {"format_type": str, "forms": {tag: unit}, "has_marker": bool}

        Only units whose XML element is still intact (i.e. before folding)
        are examined; already-folded units are ignored.
        """
        groups = {}

        for unit in self.units:
            if unit.is_plural_marker:
                base_key = unit.get_base_key()
                if base_key:
                    if base_key not in groups:
                        groups[base_key] = {
                            "format_type": "",
                            "forms": {},
                            "has_marker": True,
                        }
                    else:
                        groups[base_key]["has_marker"] = True
            elif unit.is_format_type:
                base_key = unit.get_base_key()
                if base_key:
                    if base_key not in groups:
                        groups[base_key] = {
                            "format_type": "",
                            "forms": {},
                            "has_marker": False,
                        }
                    groups[base_key]["format_type"] = unit.target or unit.source
            elif unit.is_plural_form:
                base_key = unit.get_base_key()
                plural_form = unit.get_plural_form()
                if base_key and plural_form:
                    if base_key not in groups:
                        groups[base_key] = {
                            "format_type": "",
                            "forms": {},
                            "has_marker": False,
                        }
                    groups[base_key]["forms"][plural_form] = unit

        return groups

    def _fold_plural_units(self):
        """
        Merge plural-form units into single multistring units.

        For each plural group that has at least one plural form:
        - The first unit encountered for the group becomes the *container*.
          For standard Apple XLIFF (with NSStringPluralRuleType markers) this
          will be the marker unit; for marker-less variants the first form unit.
        - All other units that belong to the same group are removed from
          ``self.units`` (their XML elements remain in the document so that
          serialisation can still find them via :meth:`_sync_plural_unit_to_xml`).
        - The container's ``_plural_source``, ``_plural_target``,
          ``_plural_base_key``, and ``format_value_type`` are set.
        - ``_plural_dirty`` is set to ``False`` (the XML is already in sync
          with the folded data after a fresh parse).
        """
        plural_groups = self._group_plural_units()
        foldable_keys = {k for k, v in plural_groups.items() if v["forms"]}

        new_units = []
        processed_keys = set()

        for unit in self.units:
            base_key = unit.get_base_key()

            if base_key not in foldable_keys:
                # Not part of a foldable plural group — keep as regular unit.
                new_units.append(unit)
                continue

            if base_key in processed_keys:
                # Subsequent units of an already-folded group: skip from self.units
                # but leave their XML elements in the document for serialize().
                continue

            # First unit of a foldable group — make it the container.
            group_data = plural_groups[base_key]
            forms = group_data["forms"]
            plural_tags = self.target_plural_tags

            source_strings = [
                forms[t].source or "" if t in forms else "" for t in plural_tags
            ]
            target_strings = [
                forms[t].target or "" if t in forms else "" for t in plural_tags
            ]

            unit._plural_source = multistring(source_strings)
            unit._plural_target = multistring(target_strings)
            unit._plural_base_key = base_key
            unit.format_value_type = group_data["format_type"]
            unit._plural_dirty = False  # XML already in sync after parse

            new_units.append(unit)
            processed_keys.add(base_key)

        self.units = new_units

    def _make_trans_unit_xml_element(self, unit_id, source_text, target_text):
        """
        Create a ``<trans-unit>`` XML element with the given id, source and target.
        """
        ns = self.namespace
        trans_unit = etree.Element(
            etree.QName(ns, "trans-unit") if ns else "trans-unit"
        )
        trans_unit.set("id", unit_id)
        setXMLspace(trans_unit, "preserve")

        src_el = etree.SubElement(
            trans_unit, etree.QName(ns, "source") if ns else "source"
        )
        src_el.text = source_text

        tgt_el = etree.SubElement(
            trans_unit, etree.QName(ns, "target") if ns else "target"
        )
        tgt_el.text = target_text

        return trans_unit

    def _sync_plural_unit_to_xml(self, unit):
        """
        Rebuild the XML elements for a plural unit.

        Removes any existing format-type / form elements for the group from
        the document body and recreates them from the unit's ``_plural_source``
        / ``_plural_target`` attributes.

        Also ensures the container XML element acts as the Apple XLIFF marker
        (id = ``base_key:dict``, source/target = ``NSStringPluralRuleType``).
        """
        base_key = unit._plural_base_key
        if base_key is None:
            return

        body = unit.xmlelement.getparent()
        if body is None:
            return

        # --- Ensure the container XML element has the marker structure ---
        unit.xmlelement.set("id", f"{base_key}:dict")
        # Update XML source/target nodes to NSStringPluralRuleType
        source_node = unit.get_source_dom()
        if source_node is None:
            source_node = unit.createlanguageNode("en", "", "source")
            unit.set_source_dom(source_node)
        source_node.text = "NSStringPluralRuleType"

        target_node = unit.get_target_dom()
        if target_node is None:
            target_node = unit.createlanguageNode("xx", "", "target")
            unit.set_target_dom(target_node)
        target_node.text = "NSStringPluralRuleType"

        # --- Remove stale format-type and form XML elements for this group ---
        marker_pos = list(body).index(unit.xmlelement)
        stale = []
        for child in body:
            child_id = child.get("id", "")
            if child_id == f"{base_key}:dict/:string":
                stale.append(child)
            elif any(
                child_id == f"{base_key}:dict/{tag}:dict/:string"
                for tag in data.cldr_plural_categories
            ):
                stale.append(child)
        for el in stale:
            body.remove(el)

        # --- Insert new format-type element ---
        format_el = self._make_trans_unit_xml_element(
            f"{base_key}:dict/:string",
            unit.format_value_type,
            unit.format_value_type,
        )
        body.insert(marker_pos + 1, format_el)

        # --- Insert new form elements ---
        plural_tags = self.target_plural_tags
        source_strs = unit._plural_source.strings if unit._plural_source else []
        target_strs = unit._plural_target.strings if unit._plural_target else []

        offset = 2
        for i, tag in enumerate(plural_tags):
            src = str(source_strs[i]) if i < len(source_strs) else ""
            tgt = str(target_strs[i]) if i < len(target_strs) else ""
            if not src and not tgt:
                continue
            form_el = self._make_trans_unit_xml_element(
                f"{base_key}:dict/{tag}:dict/:string", src, tgt
            )
            body.insert(marker_pos + offset, form_el)
            offset += 1

        unit._plural_dirty = False

    # ------------------------------------------------------------------
    # parse / serialize
    # ------------------------------------------------------------------

    def parse(self, xml) -> None:
        """Parse the Apple XLIFF file and fold plural groups."""
        super().parse(xml)
        self._fold_plural_units()

    def serialize(self, out) -> None:
        """
        Serialise to Apple XLIFF.

        Before writing the XML, any plural unit whose data has changed since
        the last parse/sync is expanded back into the marker + format-type +
        form-unit structure expected by Apple tools.
        """
        for unit in self.units:
            if unit._plural_base_key is not None and unit._plural_dirty:
                self._sync_plural_unit_to_xml(unit)
        super().serialize(out)

    # ------------------------------------------------------------------
    # Public API helpers
    # ------------------------------------------------------------------

    def _get_current_filename(self):
        """
        Return the filename of the current file section in the store.

        Falls back to the first file's name or "NoName".
        """
        if self._filename:
            return self._filename
        filenames = self.getfilenames()
        return filenames[0] if filenames else "NoName"

    def add_plural_unit(
        self, base_key, plural_strings, format_value_type="d", source_strings=None
    ):
        """
        Add a plural unit as a single merged unit with multistring source/target.

        :param base_key: Logical key, e.g. ``"shopping-list:apple"``
        :param plural_strings: A :class:`multistring` or list of plural target strings
        :param format_value_type: The NSStringFormatValueTypeKey value (e.g. ``"d"``)
        :param source_strings: Optional source strings; defaults to *plural_strings*
        """
        # Normalise inputs to lists aligned with target_plural_tags
        if isinstance(plural_strings, multistring):
            plural_strings = plural_strings.strings
        if source_strings is None:
            source_strings = plural_strings
        elif isinstance(source_strings, multistring):
            source_strings = source_strings.strings

        plural_tags = self.target_plural_tags

        def _pad(lst):
            lst = list(lst) + [""] * (len(plural_tags) - len(lst))
            return lst[: len(plural_tags)]

        plural_strings = _pad(plural_strings)
        source_strings = _pad(source_strings)

        filename = self._get_current_filename()

        # Create a single merged unit backed by a marker XML element
        marker_unit = self.addsourceunit("", filename=filename, createifmissing=True)
        marker_unit.xmlelement.set("id", f"{base_key}:dict")
        # Set XML source/target so the element is a valid XLIFF trans-unit
        marker_unit.setsource("NSStringPluralRuleType")
        marker_unit.settarget("NSStringPluralRuleType")

        # Store plural data in Python attributes
        marker_unit._plural_source = multistring(source_strings)
        marker_unit._plural_target = multistring(plural_strings)
        marker_unit._plural_base_key = base_key
        marker_unit.format_value_type = format_value_type
        marker_unit._plural_dirty = True  # XML needs format-type + form elements

    def get_plural_unit(self, base_key):
        """
        Return a merged plural unit description for *base_key*.

        For backward compatibility this returns a dict::

            {"target": multistring(...), "format_value_type": "d"}

        Returns ``None`` when *base_key* is not found.
        """
        for unit in self.units:
            if unit._plural_base_key == base_key:
                return {
                    "target": unit.target,
                    "format_value_type": unit.format_value_type,
                }
        return None

    def remove_plural_unit(self, base_key):
        """
        Remove the plural unit for *base_key* along with its XML elements.

        :returns: ``True`` if the unit was found and removed, ``False`` otherwise.
        """
        # Find the merged unit
        merged = None
        for unit in self.units:
            if unit._plural_base_key == base_key:
                merged = unit
                break

        if merged is None:
            # Fall back: look for any raw units whose base key matches
            raw_units = [u for u in self.units if u.get_base_key() == base_key]
            if not raw_units:
                return False
            for unit in raw_units:
                self.removeunit(unit)
            return True

        # Remove form / format-type XML elements from the document
        body = merged.xmlelement.getparent()
        if body is not None:
            for child in list(body):
                child_id = child.get("id", "")
                if child_id == f"{base_key}:dict/:string" or any(
                    child_id == f"{base_key}:dict/{tag}:dict/:string"
                    for tag in data.cldr_plural_categories
                ):
                    body.remove(child)

        self.removeunit(merged)
        return True


def AppleStringsXliff(inputfile=None, **kwargs):
    """Helper function to create AppleStringsXliffFile instances."""
    return AppleStringsXliffFile(inputfile, **kwargs)
