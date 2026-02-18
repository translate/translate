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

Reference: https://docs.lokalise.com/en/articles/1400816-xliff-xlf-xliff#plural-support
"""

import os
import re

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import base, xliff


class AppleStringsXliffUnit(xliff.Xliff1Unit):
    """
    A translation unit in an Apple XLIFF file.
    
    Handles both regular strings and plural forms encoded in Apple's XLIFF format.
    """
    
    format_value_type = ""
    
    def __init__(self, source, **kwargs):
        super().__init__(source, **kwargs)
        self.format_value_type = ""
    
    @property
    def is_plural_marker(self):
        """Check if this unit marks a plural variable (NSStringPluralRuleType)."""
        return self.source == "NSStringPluralRuleType"
    
    @property
    def is_format_type(self):
        """Check if this unit specifies a format value type."""
        # Use raw ID from XML element, not the combined ID from getid()
        unit_id = self.xmlelement.get("id", "")
        return unit_id.endswith(":dict/:string") and not any(
            f"/{tag}:dict/:string" in unit_id 
            for tag in data.cldr_plural_categories
        )
    
    @property
    def is_plural_form(self):
        """Check if this unit contains a plural form string."""
        # Use raw ID from XML element, not the combined ID from getid()
        unit_id = self.xmlelement.get("id", "")
        return any(
            f"/{tag}:dict/:string" in unit_id 
            for tag in data.cldr_plural_categories
        )
    
    def get_base_key(self):
        """
        Extract the base key from a plural-related ID.
        
        Example: "shopping-list:apple:dict/one:dict/:string" -> "shopping-list:apple"
        """
        # Use raw ID from XML element, not the combined ID from getid()
        unit_id = self.xmlelement.get("id", "")
        match = re.match(r"^([^:]+:[^:]+):dict", unit_id)
        if match:
            return match.group(1)
        # Check if it's a simple format string
        if ":dict" not in unit_id:
            return unit_id
        return None
    
    def get_plural_form(self):
        """
        Extract the plural form name from the ID.
        
        Example: "shopping-list:apple:dict/one:dict/:string" -> "one"
        """
        # Use raw ID from XML element, not the combined ID from getid()
        unit_id = self.xmlelement.get("id", "")
        for tag in data.cldr_plural_categories:
            pattern = f"/{tag}:dict/:string"
            if pattern in unit_id:
                return tag
        return None


class AppleStringsXliffFile(xliff.Xliff1File):
    """
    An Apple XLIFF file with support for plural strings.
    
    This format is used by Apple's localization tools and stores .stringsdict
    plural information in XLIFF trans-units with special ID naming conventions.
    """
    
    UnitClass = AppleStringsXliffUnit
    Name = "Apple XLIFF"
    Mimetypes = ["application/x-xliff+xml"]
    Extensions = ["xliff", "xlf"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plural_units = {}  # Cache of grouped plural units
    
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
        Get all supported plural tags for the target language.
        Note that 'zero' is always supported (Apple convention).
        """
        target_lang = self.gettargetlanguage()
        if target_lang is None:
            return data.cldr_plural_categories
        
        tags = self.get_plural_tags().copy()
        if "zero" not in tags:
            tags.insert(0, "zero")
        return tags
    
    def _group_plural_units(self):
        """
        Group related plural units together.
        
        Returns a dict mapping base keys (e.g., "shopping-list:apple") to
        a dict containing:
        - 'format_type': the format value type (e.g., "d")
        - 'forms': dict mapping plural tags to unit objects
        """
        groups = {}
        
        for unit in self.units:
            if unit.is_plural_marker:
                # This marks a plural variable
                base_key = unit.get_base_key()
                if base_key and base_key not in groups:
                    groups[base_key] = {'format_type': '', 'forms': {}}
            elif unit.is_format_type:
                # This specifies the format value type
                base_key = unit.get_base_key()
                if base_key:
                    if base_key not in groups:
                        groups[base_key] = {'format_type': '', 'forms': {}}
                    groups[base_key]['format_type'] = unit.target or unit.source
            elif unit.is_plural_form:
                # This is an actual plural form string
                base_key = unit.get_base_key()
                plural_form = unit.get_plural_form()
                if base_key and plural_form:
                    if base_key not in groups:
                        groups[base_key] = {'format_type': '', 'forms': {}}
                    groups[base_key]['forms'][plural_form] = unit
        
        return groups
    
    def _merge_plural_units(self):
        """
        Process all units and merge plural forms into multistring units.
        
        This converts Apple XLIFF's multiple trans-units per plural into
        single units with multistring targets.
        """
        plural_groups = self._group_plural_units()
        
        # Track which units are part of plural groups (to be removed)
        units_to_remove = set()
        
        # Create merged units for each plural group
        for base_key, group_data in plural_groups.items():
            forms = group_data['forms']
            if not forms:
                continue
            
            # Collect plural strings in the correct order
            plural_tags = self.target_plural_tags
            plural_strings = []
            
            for tag in plural_tags:
                if tag in forms:
                    unit = forms[tag]
                    plural_strings.append(unit.target or unit.source or "")
                    units_to_remove.add(id(unit))
                else:
                    plural_strings.append("")
            
            # Find or create a unit for this plural group
            # Look for the marker unit to convert it
            for unit in self.units:
                if unit.get_base_key() == base_key and unit.is_plural_marker:
                    # Convert the marker unit to hold the multistring
                    unit.target = multistring(plural_strings)
                    unit.format_value_type = group_data['format_type']
                    units_to_remove.add(id(unit))
                    
                    # Also mark the format type unit for removal
                    for u in self.units:
                        if u.get_base_key() == base_key and u.is_format_type:
                            units_to_remove.add(id(u))
                    break
        
        # Remove the individual plural form units (they're now merged)
        # Keep this commented for now - we need to think about whether to
        # keep the original structure or transform it
        # self.units = [u for u in self.units if id(u) not in units_to_remove]
    
    def parse(self, input):
        """Parse the Apple XLIFF file and process plural units."""
        super().parse(input)
        # For now, we'll keep the original structure but add methods
        # to access plural forms as multistrings when needed
        self._plural_units = self._group_plural_units()
    
    def get_plural_unit(self, base_key):
        """
        Get a merged plural unit for the given base key.
        
        Returns a dict with 'target' (multistring) and 'format_value_type' (str).
        """
        if base_key not in self._plural_units:
            return None
        
        group_data = self._plural_units[base_key]
        forms = group_data['forms']
        
        if not forms:
            return None
        
        # Collect plural strings in the correct order
        plural_tags = self.target_plural_tags
        plural_strings = []
        
        for tag in plural_tags:
            if tag in forms:
                unit = forms[tag]
                plural_strings.append(unit.target or unit.source or "")
            else:
                plural_strings.append("")
        
        return {
            'target': multistring(plural_strings),
            'format_value_type': group_data['format_type']
        }


def AppleStringsXliff(inputfile=None, **kwargs):
    """Helper function to create AppleStringsXliffFile instances."""
    return AppleStringsXliffFile(inputfile, **kwargs)
