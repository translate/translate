#
# Copyright 2025 Translate Toolkit contributors
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

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

from __future__ import annotations

import os
import re
from copy import deepcopy
from typing import IO, Any

from lxml import etree

from translate.lang import data
from translate.misc.multistring import multistring
from translate.misc.xml_helpers import (
    getText,
    getXMLspace,
    getXMLspaceInherited,
    setXMLspace,
)
from translate.storage import base, xliff


class AppleStringsXliffUnit(xliff.Xliff1Unit):
    """
    A translation unit in an Apple XLIFF file.

    Regular (non-plural) units behave identically to :class:`xliff.Xliff1Unit`.

    Plural units expose their source/target as :class:`~translate.misc.multistring.multistring`
    objects whose strings list corresponds to the target language's plural forms.
    """

    format_value_type: str = ""

    def __init__(self, source, **kwargs) -> None:
        # Initialise plural attributes BEFORE super().__init__() so that
        # self.source = source (called inside super().__init__) can set them.
        self.format_value_type = ""
        self._plural_source: multistring | None = None
        self._plural_target: multistring | None = None
        self._exposed_target: tuple[multistring, tuple[str, ...]] | None = None
        self._plural_base_key: str | None = None
        self._plural_forms: dict[str, etree._Element] = {}
        self._plural_tags: list[str] = []
        self._detached_locale: str | None = None
        self._plural_dirty: bool = False
        self._plural_dirty_targets: set[str] = set()
        self._plural_state_override: int | None = None
        super().__init__(source, **kwargs)

    def copy(self):
        if not self.hasplural():
            return super().copy()
        clone = deepcopy(self, {id(self._store): None})
        if isinstance(self._store, AppleStringsXliffFile):
            clone._remember_plural_locale(self._store)
            self._preserve_inherited_space(clone)
        return clone

    def _preserve_inherited_space(self, detached) -> None:
        for tag, form in self._plural_forms.items():
            if getXMLspace(form) is None and (space := getXMLspaceInherited(form)):
                setXMLspace(detached._plural_forms[tag], space)

    def _remember_plural_locale(self, store) -> None:
        self._detached_locale = (
            store.get_base_locale_code() if store.gettargetlanguage() else None
        )
        if not self._plural_tags and self._plural_target is not None:
            self._plural_tags = store._get_target_plural_tags(self._plural_target)

    def __eq__(self, other):
        if isinstance(other, AppleStringsXliffUnit) and (
            self.hasplural() or other.hasplural()
        ):
            return (
                super().__eq__(other)
                and self.plural_forms == other.plural_forms
                and self.source == other.source
                and self.target == other.target
                and self.format_value_type == other.format_value_type
            )
        return super().__eq__(other)

    def merge(
        self, otherunit, overwrite=False, comments=True, authoritative=False
    ) -> None:
        if (
            self.hasplural()
            and isinstance(otherunit, AppleStringsXliffUnit)
            and otherunit.hasplural()
        ):
            if overwrite or not self._has_target_text():
                if (
                    self._can_edit_plural_forms()
                    and (forms := otherunit.plural_forms) is not None
                ):
                    recipient_sources = self._source_plural_forms()
                    donor_sources = otherunit._source_plural_forms()
                    fuzzy = otherunit.isfuzzy() or any(
                        donor_sources.get(tag) != recipient_sources.get(tag)
                        for tag in forms
                    )
                    self.plural_forms = forms
                    if self._has_target_text():
                        state = self.S_NEEDS_TRANSLATION if fuzzy else self.S_TRANSLATED
                        self._plural_state_override = None
                        self._set_present_plural_state(state)
                else:
                    self.target = multistring(
                        self.get_plural_strings(
                            otherunit.target if otherunit.target is not None else ""
                        )
                    )
                    if self._has_target_text():
                        self._merge_translation_state(otherunit)
            if comments:
                self.addnote(otherunit.getnotes())
            return
        super().merge(otherunit, overwrite, comments, authoritative)

    @staticmethod
    def correctorigin(node, origin):
        """Treat Apple's bare notes as developer notes."""
        if (
            origin == "developer"
            and etree.QName(node).localname == "note"
            and not node.get("from")
        ):
            return True
        return xliff.Xliff1Unit.correctorigin(node, origin)

    def addnote(self, text, origin=None, position="append") -> None:
        """Add developer notes using Apple's bare ``note`` representation."""
        if origin == "developer":
            if position != "append":
                self.removenotes(origin=origin)
                position = "append"
            origin = None
        super().addnote(text, origin=origin, position=position)

    def _plural_form_elements(self) -> list[etree._Element]:
        """Return the XML trans-units represented by this folded plural."""
        return list(self._plural_forms.values())

    def _target_state(
        self,
        target_node: etree._Element | None,
        target_text: str | None = None,
    ) -> tuple[int, bool]:
        """Return a target's effective state and whether it was explicit."""
        if target_text is not None and not target_text:
            return self.S_UNTRANSLATED, False

        if target_node is not None:
            xml_state = target_node.get("state")
            if xml_state is not None:
                if xml_state == "new":
                    return self.S_UNTRANSLATED, True
                return self.statemap.get(xml_state, self.S_UNTRANSLATED), True

            if target_text is None:
                parent = target_node.getparent()
                xml_space = getXMLspace(
                    parent, getattr(self, "_default_xml_space", "preserve")
                )
                target_text = getText(target_node, xml_space)

        if target_text:
            return self.S_TRANSLATED, False
        return self.S_UNTRANSLATED, False

    def isblank(self) -> bool:
        blank = super().isblank()
        if not blank or not self.hasplural():
            return blank
        if self._has_target_text():
            return False
        return not any(self._source_plural_forms().values())

    def isfuzzy(self) -> bool:
        if self.hasplural():
            return not self.isapproved() and self._has_target_text()
        return super().isfuzzy()

    def _target_changed_in_place(self) -> bool:
        exposed = self._exposed_target
        return (
            exposed is not None
            and exposed[0] is self._plural_target
            and tuple(exposed[0].extra_strings) != exposed[1]
        )

    def _get_plural_forms(self) -> dict[str, str] | None:
        forms = self._stored_plural_forms()
        if self._target_changed_in_place() and self._plural_target is not None:
            tags = tuple(self._plural_tags_for_target(self._plural_target))
            return base.NamedPluralUnit._merge_positional(
                self._plural_target, tags, forms
            )
        return forms

    def _insert_form_node(self, form, role):
        node = form.makeelement(self.namespaced(role))
        if role == "target":
            # XLIFF 1.2 permits seg-source between source and target.
            for name in ("seg-source", "source"):
                previous = form.find(self.namespaced(name))
                if previous is not None:
                    previous.addnext(node)
                    return node
        form.insert(0, node)
        return node

    def _set_form_text(self, node, text):
        for child in list(node):
            node.remove(child)
        node.text = text
        if self.getNodeText(node, self._default_xml_space) != text:
            setXMLspace(node, "preserve")

    def _stored_plural_forms(self) -> dict[str, str] | None:
        if not self.hasplural() or (
            not self._plural_forms
            and not self._plural_tags_for_target(self._plural_target)
        ):
            return None
        forms = self._xml_plural_forms()
        if self._plural_dirty and self._plural_target is not None:
            tags = self._plural_tags_for_target(self._plural_target)
            strings = self._plural_target.strings
            for tag in tags[len(strings) :]:
                forms.pop(tag, None)
            for tag, text in zip(tags, strings, strict=False):
                if str(text) or tag in self._plural_dirty_targets:
                    forms[tag] = str(text)
        return forms

    def _xml_plural_forms(self) -> dict[str, str]:
        forms = {}
        for tag, form in self._plural_forms.items():
            node = form.find(self.namespaced("target"))
            if node is not None:
                forms[tag] = self.getNodeText(node, self._default_xml_space)
        return forms

    @staticmethod
    def _inline_target_edit(node, original: str, replacement: str):
        """Find the XML text slot containing a localized plain-text edit."""
        raw = str(node.xpath("string(.)"))

        def normalize(text):
            # XPath normalize-space collapses only XML whitespace.
            return re.sub(r"[ \t\r\n]+", " ", text).strip(" ")

        offset = 0
        for slot in node.xpath(".//text()"):
            prefix, suffix = raw[:offset], raw[offset + len(slot) :]
            offset += len(slot)
            boundaries = [(prefix, suffix)]
            if raw != original:
                boundaries.append((normalize(prefix), normalize(suffix)))
            for left, right in boundaries:
                end = len(replacement) - len(right)
                if (
                    end < len(left)
                    or not replacement.startswith(left)
                    or not replacement.endswith(right)
                ):
                    continue
                value = replacement[len(left) : end]
                rendered = prefix + value + suffix
                if rendered == replacement or (
                    raw != original and normalize(rendered) == replacement
                ):
                    return slot.getparent(), "tail" if slot.is_tail else "text", value
        raise ValueError("Plural edit spans inline XLIFF codes")

    def _can_edit_plural_forms(self) -> bool:
        return self._plural_base_key is not None and (
            self._store is not None or bool(self._plural_tags)
        )

    def _replace_plural_forms(self, forms: dict[str, str], *, tags=None) -> None:
        store = self._store
        if not self._can_edit_plural_forms():
            raise ValueError(
                "Attach the Apple plural group before editing named targets"
            )
        current = self._xml_plural_forms()
        if tags is None:
            tags = (
                store._get_target_plural_tags(self._plural_target)
                if store is not None
                else self._plural_tags
            )
        if (
            current == forms
            and not self._plural_dirty
            and self._plural_tags == tags
            and not self._target_changed_in_place()
        ):
            return
        inline_edits = set()
        for tag, text in forms.items():
            if tag not in data.cldr_plural_categories:
                raise ValueError(f"Unknown Apple plural category: {tag}")
            # Check XML characters before modifying siblings.
            etree.Element("target").text = text
            form = self._plural_forms.get(tag)
            if form is not None and text and current.get(tag) != text:
                node = form.find(self.namespaced("target"))
                if node is not None and len(node):
                    self._inline_target_edit(node, current[tag], text)
                    inline_edits.add(tag)

        if self._plural_dirty and store is not None:
            store._sync_plural_unit_to_xml(self)
            current = self._stored_plural_forms() or {}
        for tag in current.keys() - forms:
            form = self._plural_forms[tag]
            node = form.find(self.namespaced("target"))
            if node is not None:
                form.remove(node)
        for tag, text in forms.items():
            if current.get(tag) == text:
                continue
            if tag in inline_edits:
                node = self._plural_forms[tag].find(self.namespaced("target"))
                element, field, replacement = self._inline_target_edit(
                    node, current[tag], text
                )
                setattr(element, field, replacement)
                if self.getNodeText(node, self._default_xml_space) != text:
                    setXMLspace(node, "preserve")
                continue
            form = self._plural_forms.get(tag)
            if form is None:
                form = AppleStringsXliffFile._make_trans_unit_xml_element(
                    etree.QName(self.xmlelement).namespace,
                    f"{self._plural_base_key}:dict/{tag}:dict/:string",
                    "",
                    text,
                )
                anchor = next(reversed(self._plural_forms.values()), self.xmlelement)
                if store is not None:
                    anchor.addnext(form)
                self._plural_forms[tag] = form
            else:
                node = form.find(self.namespaced("target"))
                if node is None:
                    node = self._insert_form_node(form, "target")
                self._set_form_text(node, text)
                if not text:
                    node.attrib.pop("state", None)
                    node.attrib.pop("state-qualifier", None)
        self._plural_dirty_targets.clear()
        self._set_plural_tags(tags)
        self._plural_target = multistring([forms.get(tag, "") for tag in tags])
        self._plural_state_override = None
        self._rich_target = None
        self._invalidate_store_indexes()

    def _plural_explicit_states(self) -> dict[str, tuple[int, str | None]]:
        """Return explicit states indexed by plural tag."""
        states = {}
        for tag, form in self._plural_forms.items():
            target_node = next(
                form.iterchildren(self.namespaced("target")),
                None,
            )
            state_n, is_explicit = self._target_state(target_node)
            if is_explicit and target_node is not None:
                states[tag] = (state_n, target_node.get("state-qualifier"))
        return states

    def _source_plural_forms(self) -> dict[str, str]:
        sources = {
            tag: self.getNodeText(
                form.find(self.namespaced("source")), self._default_xml_space
            )
            or ""
            for tag, form in self._plural_forms.items()
        }
        if self._plural_source is not None:
            tags = self._plural_tags_for_target(self._plural_target)
            strings = self._plural_source.strings
            for index, tag in enumerate(tags):
                sources[tag] = strings[index] if index < len(strings) else ""
        return sources

    def _set_plural_tags(self, tags) -> None:
        if tuple(self._plural_tags) != tuple(tags):
            sources = self._source_plural_forms()
            self._plural_source = multistring([sources.get(tag, "") for tag in tags])
            self._plural_tags = list(tags)
            self._invalidate_store_indexes()

    def _plural_tags_for_target(self, target: multistring | None) -> list[str]:
        """Return stored or inferred plural tags for an in-memory target."""
        if self._plural_tags:
            return self._plural_tags
        if isinstance(self._store, AppleStringsXliffFile):
            return self._store._get_target_plural_tags(target)
        return []

    def _plural_state(self) -> tuple[int, bool]:
        """Aggregate the least-complete state across folded plural forms."""
        states = []
        has_explicit_state = False
        source_strings = self._plural_source.strings if self._plural_source else []
        target_strings = self._plural_target.strings if self._plural_target else []
        plural_tags = self._plural_tags_for_target(self._plural_target)
        for index, tag in enumerate(dict.fromkeys([*plural_tags, *self._plural_forms])):
            form = self._plural_forms.get(tag)
            source = str(source_strings[index]) if index < len(source_strings) else ""
            target = str(target_strings[index]) if index < len(target_strings) else ""
            if self._plural_dirty and tag in plural_tags and not source and not target:
                continue
            if not self._plural_dirty and form is None:
                continue

            target_node = (
                next(form.iterchildren(self.namespaced("target")), None)
                if form is not None
                else None
            )
            if self._plural_state_override is not None:
                state_n, is_explicit = self._plural_state_override, True
            else:
                state_n, is_explicit = self._target_state(
                    target_node,
                    target if tag in self._plural_dirty_targets else None,
                )
            states.append(state_n)
            has_explicit_state |= is_explicit

        if states:
            return min(states), has_explicit_state
        if self._plural_state_override is not None:
            return self._plural_state_override, True
        return (
            self.S_TRANSLATED if self.target else self.S_UNTRANSLATED,
            False,
        )

    def get_state_n(self):
        """Infer state, aggregating the least-complete folded plural form."""
        if self.hasplural():
            return self._plural_state()[0]
        return self._target_state(self.get_target_dom())[0]

    def _set_target_state(self, target_node: etree._Element, value: int) -> None:
        """Write an Apple-compatible explicit state to a target node."""
        xml_state = "new" if value == self.S_UNTRANSLATED else self.statemap_r[value]
        target_node.set("state", xml_state)

    def set_state_n(self, value) -> None:
        """Set an explicit XLIFF state without synthesizing ``approved``."""
        if value not in self.statemap_r:
            value = self.get_state_id(value)
        self.xmlelement.attrib.pop("approved", None)

        if self.hasplural():
            self._plural_state_override = value
            if self._set_present_plural_state(value):
                self._plural_dirty = True
            return

        target_node = self.get_target_dom()
        if target_node is None:
            target_node = self.createlanguageNode("xx", "", "target")
            self.set_target_dom(target_node)
        self._set_target_state(target_node, value)

    def _set_present_plural_state(self, value: int) -> bool:
        """Update existing target nodes and report whether any are missing."""
        missing_target = not self._plural_forms
        for form in self._plural_form_elements():
            form.attrib.pop("approved", None)
            target_node = next(
                form.iterchildren(self.namespaced("target")),
                None,
            )
            if target_node is None:
                missing_target = True
                continue
            self._set_target_state(target_node, value)
        return missing_target

    def isapproved(self):
        """Return approval inferred from Apple's target state."""
        return self.get_state_n() >= self.S_TRANSLATED

    def markapproved(self, value=True) -> None:
        """Map approval to target state without emitting ``approved``."""
        self.set_state_n(self.S_TRANSLATED if value else self.S_NEEDS_REVIEW)

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
    def source(self, value) -> None:
        self._invalidate_store_indexes()
        if isinstance(value, multistring):
            self._assign_plural_source(
                value, use_bound_tags=value is self._plural_source
            )
        else:
            self._plural_source = None
            self.setsource(value)

    def _assign_plural_source(
        self, value: multistring, *, use_bound_tags: bool
    ) -> None:
        if not use_bound_tags and self._plural_tags and self._can_edit_plural_forms():
            tags = self._replacement_tags(len(value.strings))
            if self._plural_tags != tags:
                # Preserve existing target labels before binding both views
                # to the destination order of this fresh source.
                self._replace_plural_forms(self._get_plural_forms() or {}, tags=tags)
        self._plural_source = value
        self._plural_dirty = True

    @property
    def target(self):
        if self._plural_target is not None:
            if self._plural_forms and (
                self._exposed_target is None
                or self._exposed_target[0] is not self._plural_target
            ):
                self._exposed_target = (
                    self._plural_target,
                    tuple(self._plural_target.extra_strings),
                )
            return self._plural_target
        return super().target

    @target.setter
    def target(self, value) -> None:
        self._assign_target(value, use_bound_tags=value is self._plural_target)

    def _replacement_tags(self, count: int) -> list[str]:
        if isinstance(self._store, AppleStringsXliffFile):
            return self._store._plural_tags_for_count(count)
        return data.get_apple_plural_tags(self._detached_locale, count)

    def _assign_target(self, value, *, use_bound_tags: bool) -> None:
        if (
            isinstance(value, multistring)
            and self._plural_forms
            and (self._store is not None or self._plural_tags)
        ):
            tags = (
                tuple(self._plural_tags)
                if use_bound_tags and self._plural_tags
                else tuple(self._replacement_tags(len(value.strings)))
            )
            if (
                tags == tuple(self._plural_tags)
                and self._plural_target is not None
                and value.strings == self._plural_target.strings
                and not self._target_changed_in_place()
            ):
                self._plural_target = value
                self._exposed_target = value, tuple(value.extra_strings)
                return
            current = self._get_plural_forms() or {}
            forms = base.NamedPluralUnit._merge_positional(value, tags, current)
            self._replace_plural_forms(forms, tags=tags)
            self._plural_dirty_targets = {
                tag
                for tag in current.keys() | forms.keys()
                if current.get(tag) != forms.get(tag)
            }
            self._exposed_target = value, tuple(value.extra_strings)
            self._plural_target = value
            return
        if isinstance(value, multistring):
            if isinstance(self._store, AppleStringsXliffFile) or self._plural_tags:
                tags = tuple(
                    self._plural_tags
                    if use_bound_tags and self._plural_tags
                    else self._replacement_tags(len(value.strings))
                )
                base.NamedPluralUnit._merge_positional(value, tags, None)
                if self._plural_tags and not use_bound_tags:
                    self._plural_tags = list(tags)
            old_target = self._plural_target
            old_strings = old_target.strings if old_target else []
            new_strings = value.strings
            plural_tags = self._plural_tags_for_target(value)
            self._plural_dirty_targets.update(
                tag
                for index, tag in enumerate(plural_tags)
                if str(old_strings[index] if index < len(old_strings) else "")
                != str(new_strings[index] if index < len(new_strings) else "")
            )
            if old_target is None or old_target != value:
                self._plural_state_override = None
            self._plural_target = value
            self._plural_dirty = True
        else:
            self._plural_target = None
            self.settarget(value)

    def hasplural(self) -> bool:
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
            self._invalidate_store_indexes()
            source = self.rich_to_multistring(value)
            self._assign_plural_source(
                source, use_bound_tags=self._rich_uses_bound_tags(source)
            )
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
            target = self.rich_to_multistring(value)
            self._assign_target(
                target, use_bound_tags=self._rich_uses_bound_tags(target)
            )
        else:
            self.set_rich_target(value)

    def _rich_uses_bound_tags(self, value: multistring) -> bool:
        count = len(value.strings)
        # A one-slot assignment can bind the locale's shorter order without
        # the optional zero. Keep it when a rich edit fills the other slots.
        return count == len(self._plural_tags) and (
            self._plural_tags == self._replacement_tags(count)
            or self._plural_tags == self._replacement_tags(1)
        )

    # getid() adds filename prefix then the raw XML id.  For plural units we
    # return the base key (without the ":dict" suffix used in the XML).
    def getid(self) -> str:
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

    def _set_local_id(self, component: str) -> None:
        self._invalidate_store_indexes()
        if self.hasplural():
            # Move the retained XML siblings to the new group before replacing
            # its base key, so serialization and removal can still find them.
            body = self.xmlelement.getparent()
            old_base_key = self._plural_base_key
            if (
                body is not None
                and old_base_key is not None
                and old_base_key != component
            ):
                for child in body:
                    child_id = child.get("id", "")
                    if (
                        child is not self.xmlelement
                        and AppleStringsXliffFile._is_plural_sibling(
                            child_id, old_base_key
                        )
                    ):
                        child.set("id", component + child_id[len(old_base_key) :])
            # Plural unit: the logical ID is the base key; update XML element id.
            self._plural_base_key = component
            self.xmlelement.set(
                "id",
                component.replace(xliff.ID_SEPARATOR, xliff.ID_SEPARATOR_SAFE)
                + ":dict",
            )
            self._plural_dirty = True
        else:
            # Non-plural or transitioning from plural to non-plural:
            # clean up stale XML sibling elements from the previous plural group.
            if self._plural_base_key is not None:
                body = self.xmlelement.getparent()
                if body is not None:
                    old_base_key = self._plural_base_key
                    for child in list(body):
                        if AppleStringsXliffFile._is_plural_sibling(
                            child.get("id", ""), old_base_key
                        ):
                            body.remove(child)
                self._plural_base_key = None
                self._plural_forms.clear()
                self._plural_tags = []
                self._plural_dirty_targets.clear()
                self._plural_state_override = None
                self._exposed_target = None
                self._plural_dirty = False
            super()._set_local_id(component)

    # ------------------------------------------------------------------
    # Helpers used during parsing to identify the role of a raw unit
    # ------------------------------------------------------------------

    @property
    def is_plural_marker(self) -> bool:
        """True if the XML source contains NSStringPluralRuleType."""
        # Read from the XML element directly so the check works before folding
        source_node = self.get_source_dom()
        if source_node is None:
            return False
        raw_src = getText(source_node, getattr(self, "_default_xml_space", "preserve"))
        return raw_src == "NSStringPluralRuleType"

    @property
    def is_format_type(self) -> bool:
        """True if this unit specifies a plural format value type (e.g. "d")."""
        unit_id = self.xmlelement.get("id", "")
        return unit_id.endswith(":dict/:string") and not any(
            f"/{tag}:dict/:string" in unit_id for tag in data.cldr_plural_categories
        )

    @property
    def is_plural_form(self) -> bool:
        """True if this unit contains a plural form string."""
        unit_id = self.xmlelement.get("id", "")
        return any(
            f"/{tag}:dict/:string" in unit_id for tag in data.cldr_plural_categories
        )

    def get_base_key(self) -> str | None:
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

    def get_plural_form(self) -> str | None:
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

    def gettargetlanguage(self) -> str | None:
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

    def _get_target_plural_tags(self, target=None) -> list[str]:
        """
        Return the plural tags for the target language.

        "zero" is included first when there is room for optional forms.
        """
        count = (
            len(self.UnitClass.get_plural_strings(target))
            if target is not None
            else None
        )
        return self._plural_tags_for_count(count)

    def _plural_tags_for_count(self, count: int | None) -> list[str]:
        locale = (
            self.get_base_locale_code()
            if self.gettargetlanguage() is not None
            else None
        )
        return data.get_apple_plural_tags(locale, count)

    @property
    def target_plural_tags(self) -> list[str]:
        return self._get_target_plural_tags()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_plural_form_sibling(child_id: str, base_key: str) -> bool:
        """Return whether *child_id* is a plural form for *base_key*."""
        return any(
            child_id == f"{base_key}:dict/{tag}:dict/:string"
            for tag in data.cldr_plural_categories
        )

    @classmethod
    def _is_plural_sibling(cls, child_id: str, base_key: str) -> bool:
        """
        Return ``True`` if *child_id* belongs to the plural group *base_key*.

        This covers the format-type element (``base_key:dict/:string``) and all
        per-form elements (``base_key:dict/<tag>:dict/:string``).
        """
        if child_id == f"{base_key}:dict/:string":
            return True
        return cls._is_plural_form_sibling(child_id, base_key)

    def _group_plural_units(self) -> dict[str, Any]:
        """
        Scan *raw* units (as produced by the parent parser) and group them.

        Returns a dict:
          base_key -> {"format_type": str, "forms": {tag: unit}, "has_marker": bool}

        Only units whose XML element is still intact (i.e. before folding)
        are examined; already-folded units are ignored.
        """
        groups: dict[str, Any] = {}

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

    def _fold_plural_units(self) -> None:
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
        processed_keys: set[str] = set()

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
            unit._plural_forms = {tag: form.xmlelement for tag, form in forms.items()}
            unit._plural_tags = plural_tags
            unit._plural_dirty_targets.clear()
            unit.format_value_type = group_data["format_type"]
            unit._plural_dirty = False  # XML already in sync after parse

            new_units.append(unit)
            processed_keys.add(base_key)

        self.units = new_units

    @staticmethod
    def _make_trans_unit_xml_element(
        ns, unit_id: str, source_text: str, target_text: str
    ):
        """Create a ``<trans-unit>`` XML element with the given id, source and target."""
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

    def _sync_plural_unit_to_xml(self, unit: AppleStringsXliffUnit) -> None:
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

        explicit_states = unit._plural_explicit_states()

        # A marker-less catalog can use the first form as the container.
        # Keep a copy of that form before normalizing the marker.
        retained = dict(unit._plural_forms)
        for tag, form in retained.items():
            if form is unit.xmlelement or form.getparent() is not body:
                copied = deepcopy(form)
                old_ns = etree.QName(form).namespace
                if old_ns != self.namespace:
                    for child in copied.iter(etree.Element):
                        name = etree.QName(child)
                        if name.namespace == old_ns:
                            child.tag = unit.namespaced(name.localname)
                    etree.cleanup_namespaces(copied)
                retained[tag] = copied

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
        stale = [
            child
            for child in body
            if self._is_plural_sibling(child.get("id", ""), base_key)
        ]
        for el in stale:
            body.remove(el)

        # --- Insert new format-type element ---
        format_el = self._make_trans_unit_xml_element(
            self.namespace,
            f"{base_key}:dict/:string",
            unit.format_value_type,
            unit.format_value_type,
        )
        body.insert(marker_pos + 1, format_el)

        # --- Insert new form elements ---
        plural_tags = unit._plural_tags_for_target(unit._plural_target)
        source_strs = unit._plural_source.strings if unit._plural_source else []
        target_strs = unit._plural_target.strings if unit._plural_target else []

        offset = 2
        plural_forms = {}
        for i, tag in enumerate(plural_tags):
            src = str(source_strs[i]) if i < len(source_strs) else ""
            tgt = str(target_strs[i]) if i < len(target_strs) else ""
            form_el = retained.get(tag)
            form_id = f"{base_key}:dict/{tag}:dict/:string"
            if form_el is None:
                if not src and not tgt:
                    continue
                form_el = self._make_trans_unit_xml_element(
                    self.namespace, form_id, src, tgt
                )
            else:
                form_el.set("id", form_id)
                for role, text in (("source", src), ("target", tgt)):
                    node = form_el.find(unit.namespaced(role))
                    needs_target = (
                        role == "target" and unit._plural_state_override is not None
                    )
                    if node is None:
                        if not text and not needs_target:
                            continue
                        node = unit._insert_form_node(form_el, role)
                    if unit.getNodeText(node, unit._default_xml_space) != text:
                        unit._set_form_text(node, text)
            explicit_metadata = explicit_states.get(tag)
            explicit_state = unit._plural_state_override
            state_qualifier = (
                explicit_metadata[1] if explicit_metadata is not None else None
            )
            if explicit_state is None and (
                tag not in unit._plural_dirty_targets or tgt
            ):
                explicit_state = (
                    explicit_metadata[0] if explicit_metadata is not None else None
                )
            if explicit_state is not None:
                target_node = next(
                    form_el.iterchildren(unit.namespaced("target")),
                )
                unit._set_target_state(target_node, explicit_state)
                if state_qualifier is not None:
                    target_node.set("state-qualifier", state_qualifier)
            elif tag in unit._plural_dirty_targets and not tgt:
                node = form_el.find(unit.namespaced("target"))
                if node is not None:
                    node.attrib.pop("state", None)
                    node.attrib.pop("state-qualifier", None)
            body.insert(marker_pos + offset, form_el)
            plural_forms[tag] = form_el
            offset += 1

        for tag, form in retained.items():
            if tag not in plural_tags:
                form.set("id", f"{base_key}:dict/{tag}:dict/:string")
                if unit._plural_state_override is not None:
                    target_node = form.find(unit.namespaced("target"))
                    if target_node is None:
                        target_node = unit._insert_form_node(form, "target")
                    unit._set_target_state(target_node, unit._plural_state_override)
                body.insert(marker_pos + offset, form)
                offset += 1
                plural_forms[tag] = form

        unit._plural_forms = plural_forms
        unit._plural_tags = plural_tags
        unit._plural_dirty_targets.clear()
        unit._plural_dirty = False

    def addunit(self, unit, new=True) -> None:
        if new and isinstance(unit.target, multistring) and not unit._plural_forms:
            tags = tuple(self._get_target_plural_tags(unit.target))
            base.NamedPluralUnit._merge_positional(unit.target, tags, None)
        super().addunit(unit, new)
        if new and unit._plural_forms:
            self._sync_plural_unit_to_xml(unit)

    def removeunit(self, unit: AppleStringsXliffUnit) -> None:
        """Remove a unit; for plural units also removes their sibling XML elements."""
        if unit.hasplural():
            unit._remember_plural_locale(self)
            unit._preserve_inherited_space(unit)
        if unit._plural_base_key is not None:
            base_key = unit._plural_base_key
            body = unit.xmlelement.getparent()
            if body is not None:
                for child in list(body):
                    if child is not unit.xmlelement and self._is_plural_sibling(
                        child.get("id", ""), base_key
                    ):
                        body.remove(child)
        super().removeunit(unit)

    # ------------------------------------------------------------------
    # parse / serialize
    # ------------------------------------------------------------------

    def parse(self, xml) -> None:
        """Parse the Apple XLIFF file and fold plural groups."""
        super().parse(xml)
        self._fold_plural_units()

    def serialize(self, out: IO[bytes]) -> None:
        """
        Serialise to Apple XLIFF.

        Before writing the XML, any plural unit whose data has changed since
        the last parse/sync is expanded back into the marker + format-type +
        form-unit structure expected by Apple tools.
        """
        for unit in self.units:
            if unit._target_changed_in_place():
                target = unit.target
                unit._replace_plural_forms(
                    unit._get_plural_forms(), tags=unit._plural_tags_for_target(target)
                )
                # Keep the legacy target reference live across a save.
                unit._plural_target = target
                unit._exposed_target = target, tuple(target.extra_strings)
            if unit._plural_base_key is not None and unit._plural_dirty:
                self._sync_plural_unit_to_xml(unit)
        super().serialize(out)


def AppleStringsXliff(inputfile=None, **kwargs):
    """Helper function to create AppleStringsXliffFile instances."""
    return AppleStringsXliffFile(inputfile, **kwargs)
