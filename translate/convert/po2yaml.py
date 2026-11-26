#
# Copyright 2017 Zuza Software Foundation
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
Convert Gettext PO localization files to YAML files.

See: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/yaml2po.html
for examples and usage instructions.
"""

import gettext
from datetime import date
from functools import cached_property

from babel import Locale, UnknownLocaleError
from ruamel.yaml.comments import CommentedMap

from translate.convert import convert
from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import po, yaml


def _catalog_plural_tags(
    locale: str | None, count: str | None, expression: str | None
) -> list[str]:
    """Identify PO positions by comparing integer examples under the two rules."""
    tags = data.get_gettext_plural_tags(locale)
    if count is None and expression is None:
        return tags
    count = (count or "").strip()
    if (
        not count
        or not expression
        or not count.isdecimal()
        or not 1 <= int(count) <= len(data.cldr_plural_categories)
    ):
        raise ValueError("Invalid Plural-Forms header")
    size = int(count)
    if size == 1:
        return ["other"]
    normalized = data._normalize_to_underscore(locale or "en")
    base = normalized.split("_")[0]
    language = data.get_language(locale or "en") or data.get_language(base)
    index = gettext.c2py(expression)
    # Include representatives for modulus-100 rules and the Romance million category.
    samples = [
        (number, index(number))
        for number in (*range(201), 999999, 1000000, 1000001, 2000000)
    ]

    def match(rule):
        labels = {}
        for number, position in samples:
            tag = rule(number)
            if not 0 <= position < size or labels.setdefault(position, tag) != tag:
                return None
        if len(set(labels.values())) == size:
            return [labels[i] for i in range(size)]
        return None

    if language is not None and size == len(tags):
        default_index = gettext.c2py("n != 1" if normalized == "pt_pt" else language[2])
        legacy = match(lambda number: tags[default_index(number)])
        if legacy is not None:
            return legacy
    try:
        rule = Locale.parse(normalized).plural_form
    except (UnknownLocaleError, ValueError) as error:
        raise ValueError(f"No plural category mapping for {locale}") from error
    result = match(rule)
    if result is None:
        raise ValueError(f"Plural-Forms indexes do not match categories for {locale}")
    return result


class po2yaml:
    """Convert a PO file and a template YAML file to a YAML file."""

    SourceStoreClass: type[po.pofile] = po.pofile
    TargetStoreClass: type[yaml.YAMLFile] = yaml.YAMLFile
    TargetUnitClass: type[yaml.YAMLUnit] = yaml.YAMLUnit
    MissingTemplateMessage = "A template YAML file must be provided."

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        include_fuzzy=False,
        output_threshold=None,
        personality="default",
    ) -> None:
        """Initialize the converter."""
        if template_file is None:
            raise ValueError(self.MissingTemplateMessage)

        if personality == "ruby":
            self.TargetStoreClass = yaml.RubyYAMLFile
            self.TargetUnitClass = yaml.RubyYAMLUnit

        self.source_store = self.SourceStoreClass(input_file)
        target_language = None

        self.should_output_store = convert.should_output_store(
            self.source_store, output_threshold
        )
        if self.should_output_store:
            self.include_fuzzy = include_fuzzy

            self.output_file = output_file
            self.template_store = self.TargetStoreClass(template_file)
            if personality == "ruby":
                target_language = (
                    self.source_store.gettargetlanguage()
                    or self.template_store.gettargetlanguage()
                )

        if issubclass(self.TargetStoreClass, yaml.RubyYAMLFile):
            self.target_store = self.TargetStoreClass(targetlanguage=target_language)
        else:
            self.target_store = self.TargetStoreClass()

    @cached_property
    def _target_plural_tags(self):
        return _catalog_plural_tags(
            self.target_store.gettargetlanguage(), *self.source_store.getheaderplural()
        )

    def convert_unit(
        self, unit: po.pounit, unit_id: str | None = None
    ) -> yaml.YAMLUnit:
        """Convert a source format unit to a target format unit."""
        use_target = unit.istranslated() or (unit.isfuzzy() and self.include_fuzzy)
        if (
            use_target
            and issubclass(self.TargetUnitClass, yaml.RubyYAMLUnit)
            and isinstance(unit.target, multistring)
            and not any(unit.target.strings)
        ):
            use_target = False
        target_unit = self.TargetUnitClass(
            source=unit.target if use_target else unit.source,
        )
        if isinstance(target_unit, yaml.RubyYAMLUnit) and isinstance(
            target_unit.target, multistring
        ):
            # PO source positions are msgid and msgid_plural, also for fuzzy
            # translations excluded from import. The header describes msgstr only.
            tags = self._target_plural_tags if use_target else ["one", "other"]
            values = target_unit.target.strings
            if len(values) > len(tags):
                raise ValueError(
                    "More PO plural translations than target locale categories"
                )
            forms = {
                tag: str(value)
                for tag, value in zip(tags, values, strict=False)
                if value or not use_target
            }
            target_unit.set_plural_projection(forms, tags[: len(values)])
        target_unit.setid(unit_id if unit_id is not None else unit.getlocations()[0])
        target_unit.addnote(unit.getnotes("developer"), "developer")
        return target_unit

    def merge_stores(self) -> None:
        """
        Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        self.source_store.makeindex()
        unit_paths = set()

        for template_unit in self.template_store.units:
            template_unit_id = template_unit.getid()

            if template_unit_id in self.source_store.locationindex:
                input_unit = self.source_store.locationindex[template_unit_id]
                target_unit = self.convert_unit(input_unit, template_unit_id)
                self.target_store.addunit(target_unit)
                unit_paths.add(tuple(target_unit.get_unitid().parts))

        self._keep_untranslatable_values(unit_paths)

    def _keep_untranslatable_values(self, unit_paths) -> None:
        """
        Copy the template's float and date values, which have no unit, to the output.

        The keys are laid out in template order first, so the units fill them in place.
        """
        parent_paths = {path[:i] for path in unit_paths for i in range(1, len(path))}

        def layout(node, path):
            out = CommentedMap()
            # merged items are skipped, as the parser does; they have no units of their own
            items = (
                node.non_merged_items()
                if hasattr(node, "non_merged_items")
                else node.items()
            )
            for key, value in items:
                # unit paths come from the PO locations, where every key is a string
                child = (*path, ("key", str(key)))
                if child in unit_paths or child in parent_paths:
                    key = str(key)
                if isinstance(value, (float, date)):
                    out[key] = value
                elif child in unit_paths:
                    out[key] = None
                elif isinstance(value, dict):
                    nested = layout(value, child)
                    if nested or child in parent_paths:
                        out[key] = nested
                elif child in parent_paths:
                    out[key] = None
            return out

        template_root = self.template_store.preprocess(self.template_store._original)
        target_root = self.target_store.preprocess(self.target_store._original)
        if isinstance(template_root, dict) and isinstance(target_root, dict):
            target_root.update(layout(template_root, ()))

    def run(self) -> int:
        """Run the converter."""
        if not self.should_output_store:
            return 0

        self.merge_stores()
        self.target_store.serialize(self.output_file)
        return 1


def run_converter(
    inputfile,
    outputfile,
    templatefile=None,
    includefuzzy=False,
    outputthreshold=None,
    personality="default",
):
    """Wrapper around converter."""
    return po2yaml(
        inputfile, outputfile, templatefile, includefuzzy, outputthreshold, personality
    ).run()


formats = (
    (("po", "yml"), ("yml", run_converter)),
    ("po", ("yml", run_converter)),
    (("po", "yaml"), ("yaml", run_converter)),
    ("po", ("yaml", run_converter)),
)


def main(argv=None) -> None:
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.add_option(
        "",
        "--personality",
        dest="personality",
        default="default",
        type="choice",
        choices=["default", "ruby"],
        help="override the output YAML format: default, ruby (for Ruby on Rails YAML files with a language root node, e.g. 'en:' or 'ca:')",
        metavar="TYPE",
    )
    parser.passthrough.append("personality")
    parser.run(argv)


if __name__ == "__main__":
    main()
