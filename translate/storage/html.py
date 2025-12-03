#
# Copyright 2004-2006,2008 Zuza Software Foundation
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
#

"""module for parsing html files for translation."""

import html.parser
import re
from html.entities import html5

from translate.lang.data import is_rtl
from translate.storage import base
from translate.storage.base import ParseError

# Override the piclose tag from simple > to ?> otherwise we consume HTML
# within the processing instructions
html.parser.piclose = re.compile(r"\?>")


class htmlunit(base.TranslationUnit):
    """A unit of translatable/localisable HTML content."""

    def __init__(self, source=None):
        super().__init__(source)
        self.locations = []
        self._context = ""

    def addlocation(self, location):
        self.locations.append(location)

    def getlocations(self):
        """Get the list of locations for this unit."""
        return self.locations

    def getcontext(self):
        """Get the message context."""
        return self._context

    def setcontext(self, context):
        """Set the message context."""
        self._context = context or ""

    def getid(self):
        """Returns a unique identifier for this unit."""
        if self._context:
            return f"{self._context}\04{self.source}"
        return self.source


class htmlfile(html.parser.HTMLParser, base.TranslationStore):
    UnitClass = htmlunit

    TRANSLATABLE_ELEMENTS = [
        "address",
        "article",
        "aside",
        "blockquote",
        "button",
        "caption",
        "dd",
        "dt",
        "div",
        "figcaption",
        "footer",
        "header",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "label",
        "li",
        "main",
        "nav",
        "option",
        "p",
        "pre",
        "section",
        "td",
        "th",
        "title",
    ]
    """These HTML elements (tags) will be extracted as translation units, unless
    they lack translatable text content.
    In case one translatable element is embedded in another, the outer translation
    unit will be split into the parts before and after the inner translation unit."""

    TRANSLATABLE_ATTRIBUTES = [
        "abbr",  # abbreviation for a table header cell
        "alt",
        "lang",  # only for the html element -- see extract_translatable_attributes()
        "summary",
        "title",  # tooltip text for an element
        "value",
    ]
    """Text from these HTML attributes will be extracted as translation units.
    Note: the content attribute of meta tags is a special case."""

    TRANSLATABLE_METADATA = [
        "description",
        "keywords",
        "og:title",
        "og:description",
        "og:site_name",
        "twitter:title",
        "twitter:description",
    ]
    """Document metadata from meta elements with these names will be extracted as translation units.
    Includes standard meta tags and common social media tags (Open Graph and Twitter Cards).
    Reference `<https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name>`_"""

    EMPTY_HTML_ELEMENTS = [
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]
    """An empty element is an element that cannot have any child nodes (i.e., nested
    elements or text nodes). In HTML, using a closing tag on an empty element is
    usually invalid.
    Reference `<https://developer.mozilla.org/en-US/docs/Glossary/Empty_element>`_"""

    WHITESPACE_RE = re.compile(r"\s+")

    LEADING_WHITESPACE_RE = re.compile(r"^(\s+)")

    TRAILING_WHITESPACE_RE = re.compile(r"(\s+)$")

    ENCODING_RE = re.compile(
        rb"""<meta.*
                                content.*=.*?charset=\s*?
                                ([^\s]*)
                                \s*?["']\s*?>
                             """,
        re.VERBOSE | re.IGNORECASE,
    )

    def __init__(self, inputfile=None, callback=None):
        super().__init__(convert_charrefs=False)
        base.TranslationStore.__init__(self)

        # store parameters
        self.filename = getattr(inputfile, "name", None)
        if callback is None:
            self.callback = self._simple_callback
        else:
            self.callback = callback

        # initialize state
        self.filesrc = ""
        self.tag_path = []
        self.tu_content = []
        self.tu_location = None
        self.ignore_depth = 0  # Track nesting level of ignored elements
        self.comment_ignore = False  # Track if inside <!-- translate:off -->
        self.ignore_tag_stack = []  # Track which tags have ignore attribute
        self.ancestor_id_stack = []  # stack of ancestor ids (top is nearest)
        self._id_pushed_stack = []  # parallel to tag stack: did this element push an id?
        self._id_depth_stack = []  # indices into tag_path where ids were pushed
        self._id_pos_stack = []  # positions (line, col) where ancestor ids start
        self._ancestor_id_label_stack = []  # labels for ancestor ids (id or id:line-col)
        self._id_seen = set()  # track seen ids to disambiguate labels
        self._units_by_source = {}  # Track units by normalized source to add context only when needed for disambiguation

        # parse
        if inputfile is not None:
            htmlsrc = inputfile.read()
            inputfile.close()
            self.parse(htmlsrc)

    @staticmethod
    def _simple_callback(string):
        return string

    def guess_encoding(self, htmlsrc):
        """
        Returns the encoding of the html text.

        We look for 'charset=' within a meta tag to do this.
        """
        result = self.ENCODING_RE.findall(htmlsrc)
        if result:
            self.encoding = result[0].decode("ascii")
        return self.encoding

    def do_encoding(self, htmlsrc):
        """Return the html text properly encoded based on a charset."""
        self.guess_encoding(htmlsrc)
        return htmlsrc.decode(self.encoding)

    def parse(self, htmlsrc):
        htmlsrc = self.do_encoding(htmlsrc)
        self.feed(htmlsrc)

    def is_extraction_ignored(self):
        """Check if we're currently in an ignored section."""
        return self.ignore_depth > 0 or self.comment_ignore

    def begin_translation_unit(self):
        # at the start of a translation unit:
        # this interrupts any translation unit in progress, so process the queue
        # and prepare for the new.
        self.emit_translation_unit()
        self.tu_content = []
        self.tu_location = "{}+{}:{}-{}".format(
            self.filename,
            ".".join(self.tag_path),
            self.getpos()[0],
            self.getpos()[1] + 1,
        )

    def end_translation_unit(self):
        # at the end of a translation unit:
        # process the queue and reset state.
        self.emit_translation_unit()
        self.tu_content = []
        self.tu_location = None

    def append_markup(self, markup):
        # if within a translation unit: add to the queue to be processed later.
        # otherwise handle immediately.
        if self.tu_location:
            self.tu_content.append(markup)
        else:
            self.emit_attribute_translation_units(markup)
            self.filesrc += markup["html_content"]

    def emit_translation_unit(self):
        # If we're in an ignored section, just output the raw content
        if self.is_extraction_ignored():
            for markup in self.tu_content:
                self.filesrc += markup["html_content"]
            return

        # scan through the queue:
        # - find the first and last translatable markup elements: the captured
        #   interval [start, end)
        # - match start and end tags
        start = 0
        end = 0
        tagstack = []
        tagmap = {}
        tag = None
        do_normalize = True
        for pos, content in enumerate(self.tu_content):
            if content["type"] != "endtag" and tag in self.EMPTY_HTML_ELEMENTS:
                match = tagstack.pop()
                tag = None

            if self.has_translatable_content(content):
                if end == 0:
                    start = pos
                end = pos + 1
            elif content["type"] == "starttag":
                tagstack.append(pos)
                tag = content["tag"]
                if tag == "pre":
                    do_normalize = False
            elif content["type"] == "endtag":
                if tagstack:
                    match = tagstack.pop()
                    tagmap[match] = pos
                    tagmap[pos] = match
                tag = None

        # if no translatable content found: process all the content in the queue
        # as if the translation unit didn't exist.
        if end == 0:
            for markup in self.tu_content:
                self.emit_attribute_translation_units(markup)
                self.filesrc += markup["html_content"]
            return

        # scan the start and end tags captured between translatable content;
        # extend the captured interval to include the matching tags
        for pos in range(start + 1, end - 1):
            if self.tu_content[pos]["type"] in {"starttag", "endtag"} and pos in tagmap:
                match = tagmap[pos]
                start = min(start, match)
                end = max(end, match + 1)

        # emit leading uncaptured markup elements
        for markup in self.tu_content[0:start]:
            if markup["type"] != "comment":
                self.emit_attribute_translation_units(markup)
                self.filesrc += markup["html_content"]

        # emit captured markup elements
        if start < end:
            html_content = []
            for markup in self.tu_content[start:end]:
                if markup["type"] != "comment":
                    if "untranslated_html" in markup:
                        html_content.append(markup["untranslated_html"])
                    else:
                        html_content.append(markup["html_content"])
            html_content = "".join(html_content)
            if do_normalize:
                normalized_content = self.WHITESPACE_RE.sub(" ", html_content.strip())
            else:
                normalized_content = html_content.strip()
            assert normalized_content  # shouldn't be here otherwise

            unit = self.addsourceunit(normalized_content)
            unit.addlocation(self.tu_location)

            # Determine context from data-translate-context (outermost wins)
            # tu_content starts at the unit's opening tag, so the first
            # translate_context encountered is the correct one.
            context = next(
                (
                    m["translate_context"]
                    for m in self.tu_content
                    if "translate_context" in m
                ),
                None,
            )
            if context:
                unit.setcontext(context)
            # If no explicit context, capture a context hint (from id/ancestor) for potential disambiguation
            context_hint = None
            if not context:
                context_hint = next(
                    (m["context_hint"] for m in self.tu_content if "context_hint" in m),
                    None,
                )
            # Register the unit for potential disambiguation using context hints
            self._register_unit_for_disambiguation(
                unit, normalized_content, context_hint
            )

            # Extract comment text from HTML comment elements within the translation unit
            comments = [
                markup["note"]
                for markup in self.tu_content
                if markup["type"] == "comment"
            ]

            # Extract translator comments from data-translate-comment attributes on any tags within the translation unit
            translate_comments = [
                markup["translate_comment"]
                for markup in self.tu_content
                if "translate_comment" in markup
            ]

            # Combine and add all comments to the unit
            all_comments = comments + translate_comments
            if all_comments:
                unit.addnote("\n".join(all_comments), origin="source code")

            html_content = (
                self.get_leading_whitespace(html_content)
                + self.callback(normalized_content)
                + self.get_trailing_whitespace(html_content)
            )
            self.filesrc += html_content

        # emit trailing uncaptured markup elements
        for markup in self.tu_content[end : len(self.tu_content)]:
            if markup["type"] != "comment":
                self.emit_attribute_translation_units(markup)
                self.filesrc += markup["html_content"]

    @staticmethod
    def has_translatable_content(markup):
        # processing instructions count as translatable content, because PHP
        return markup["type"] in {"data", "pi"} and markup["html_content"].strip()

    def extract_translatable_attributes(self, tag, attrs):
        # Don't extract attributes if we're in an ignored section
        if self.is_extraction_ignored():
            return []

        result = []
        if tag == "meta":
            tu = self.create_metadata_attribute_tu(attrs)
            if tu:
                result.append(tu)
        else:
            for attrname, attrvalue in attrs:
                if (
                    attrname in self.TRANSLATABLE_ATTRIBUTES
                    and self.translatable_attribute_matches_tag(attrname, tag)
                ):
                    tu = self.create_attribute_tu(attrname, attrvalue)
                    if tu:
                        result.append(tu)
        return result

    def create_metadata_attribute_tu(self, attrs):
        attrs_dict = dict(attrs)
        # Check both 'name' and 'property' attributes (Open Graph uses 'property')
        name = attrs_dict.get("name", "").lower()
        if not name:
            name = attrs_dict.get("property", "").lower()
        if name in self.TRANSLATABLE_METADATA and "content" in attrs_dict:
            return self.create_attribute_tu("content", attrs_dict["content"])
        return None

    @staticmethod
    def translatable_attribute_matches_tag(attrname, tag):
        if attrname == "lang":
            return tag == "html"
        return True

    def create_attribute_tu(self, attrname, attrvalue):
        normalized_value = self.WHITESPACE_RE.sub(" ", attrvalue).strip()
        if normalized_value:
            return {
                "html_content": normalized_value,
                "attrname": attrname,
                "location": "{}+{}{}:{}-{}".format(
                    self.filename,
                    ".".join(self.tag_path),
                    f"[{attrname}]",
                    self.getpos()[0],
                    self.getpos()[1] + 1,
                ),
            }
        return None

    def emit_attribute_translation_units(self, markup):
        if "attribute_tus" in markup:
            for tu in markup["attribute_tus"]:
                unit = self.addsourceunit(tu["html_content"])
                unit.addlocation(tu["location"])
                # Attribute context: prefer explicit translate_context; otherwise use context_hint only if needed
                attr_suffix = f"[{tu.get('attrname')}]" if tu.get("attrname") else ""
                explicit = markup.get("translate_context")
                if explicit:
                    unit.setcontext(f"{explicit}{attr_suffix}")
                    self._register_unit_for_disambiguation(
                        unit, tu["html_content"], None
                    )
                else:
                    hint_base = markup.get("context_hint")
                    hint = f"{hint_base}{attr_suffix}" if hint_base else None
                    self._register_unit_for_disambiguation(
                        unit, tu["html_content"], hint
                    )

    def translate_attributes(self, tag, attrs):
        if not attrs:
            return []
        result = []
        translated_lang = None

        # First pass: check if lang is being translated on html tag
        if tag == "html":
            attrs_dict = dict(attrs)
            if "lang" in attrs_dict:
                normalized_value = self.WHITESPACE_RE.sub(
                    " ", attrs_dict["lang"]
                ).strip()
                translated_value = self.callback(normalized_value)
                if translated_value != normalized_value:
                    translated_lang = translated_value

        for attrname, attrvalue in attrs:
            # When translating the lang attribute on the <html> tag, we intentionally discard
            # any existing dir attribute and set it based on the translated language below.
            # This ensures dir reflects the text directionality of the target language.
            if tag == "html" and attrname == "dir" and translated_lang:
                continue
            if attrvalue:
                # Special handling for meta tag content attribute
                if tag == "meta" and attrname == "content":
                    # Check both 'name' and 'property' attributes
                    attrs_dict = dict(attrs)
                    name = attrs_dict.get("name", "").lower()
                    if not name:
                        name = attrs_dict.get("property", "").lower()
                    if name in self.TRANSLATABLE_METADATA:
                        normalized_value = self.WHITESPACE_RE.sub(
                            " ", attrvalue
                        ).strip()
                        translated_value = self.callback(normalized_value)
                        if translated_value != normalized_value:
                            result.append((attrname, translated_value))
                            continue
                # Only translate attributes that are translatable for this specific tag
                if (
                    attrname in self.TRANSLATABLE_ATTRIBUTES
                    and self.translatable_attribute_matches_tag(attrname, tag)
                ):
                    normalized_value = self.WHITESPACE_RE.sub(" ", attrvalue).strip()
                    translated_value = self.callback(normalized_value)
                    if translated_value != normalized_value:
                        result.append((attrname, translated_value))
                        continue
            result.append((attrname, attrvalue))

        # Set dir attribute on html tag when lang is being translated
        if tag == "html" and translated_lang:
            result.append(("dir", "rtl" if is_rtl(translated_lang) else "ltr"))

        return result

    @staticmethod
    def create_start_tag(tag, attrs=None, startend=False):
        attr_strings = []
        attrs = attrs or []
        for attrname, attrvalue in attrs:
            if attrvalue is None:
                attr_strings.append(f" {attrname}")
            else:
                attr_strings.append(f' {attrname}="{attrvalue}"')
        return "<{}{}{}>".format(tag, "".join(attr_strings), " /" if startend else "")

    def auto_close_empty_element(self):
        if self.tag_path and self.tag_path[-1] in self.EMPTY_HTML_ELEMENTS:
            self.tag_path.pop()

    def get_leading_whitespace(self, text: str):
        match = self.LEADING_WHITESPACE_RE.search(text)
        return match.group(1) if match else ""

    def get_trailing_whitespace(self, text: str):
        match = self.TRAILING_WHITESPACE_RE.search(text)
        return match.group(1) if match else ""

    # From here on below, follows the methods of the HTMLParser

    def handle_starttag(self, tag, attrs):
        self.auto_close_empty_element()
        self.tag_path.append(tag)

        # Check for data-translate-ignore attribute
        attrs_dict = dict(attrs)
        has_ignore_attr = "data-translate-ignore" in attrs_dict

        if has_ignore_attr:
            self.ignore_depth += 1
            self.ignore_tag_stack.append(tag)

        # Only begin translation unit if not in ignored section
        if tag in self.TRANSLATABLE_ELEMENTS and not self.is_extraction_ignored():
            self.begin_translation_unit()

        translated_attrs = self.translate_attributes(tag, attrs)
        markup = {
            "type": "starttag",
            "tag": tag,
            "html_content": self.create_start_tag(tag, translated_attrs),
            "untranslated_html": self.create_start_tag(tag, attrs),
            "attribute_tus": self.extract_translatable_attributes(tag, attrs),
        }

        # Extract data-translate-comment attribute
        if "data-translate-comment" in attrs_dict:
            markup["translate_comment"] = attrs_dict["data-translate-comment"]

        # Extract data-translate-context attribute
        if "data-translate-context" in attrs_dict:
            context_raw = attrs_dict.get("data-translate-context") or ""
            context_value = self.WHITESPACE_RE.sub(" ", context_raw).strip()
            if context_value:
                markup["translate_context"] = context_value
            # Even with explicit context, record that no id was pushed
            self._id_pushed_stack.append(False)
        elif "id" in attrs_dict:
            # Fallback: use element id as context if present, prefixed with filename
            id_raw = attrs_dict.get("id") or ""
            id_value = self.WHITESPACE_RE.sub(" ", id_raw).strip()
            if id_value:
                id_line, id_col = self.getpos()[0], self.getpos()[1] + 1
                # Determine label for ancestor path hints
                if id_value in getattr(self, "_id_seen", set()):
                    id_label = f"{id_value}:{id_line}-{id_col}"
                    markup["context_hint"] = (
                        f"{self.filename}+{id_value}:{id_line}-{id_col}"
                    )
                else:
                    id_label = id_value
                    markup["context_hint"] = f"{self.filename}:{id_value}"
                    self._id_seen.add(id_value)
                self.ancestor_id_stack.append(id_value)
                self._ancestor_id_label_stack.append(id_label)
                self._id_pushed_stack.append(True)
                self._id_depth_stack.append(len(self.tag_path) - 1)
                self._id_pos_stack.append((id_line, id_col))
        else:
            # No explicit context and no own id; if within ancestor with id, use path
            ancestor_id = self.ancestor_id_stack[-1] if self.ancestor_id_stack else None
            if ancestor_id:
                line, col = self.getpos()[0], self.getpos()[1] + 1
                # Build relative tag path from nearest id ancestor depth
                id_depth = self._id_depth_stack[-1] if self._id_depth_stack else -1
                rel_tags = self.tag_path[id_depth + 1 :]
                ancestor_label = (
                    self._ancestor_id_label_stack[-1]
                    if self._ancestor_id_label_stack
                    else ancestor_id
                )
                path = (
                    ".".join([ancestor_label, *rel_tags])
                    if rel_tags
                    else ancestor_label
                )
                ancestor_line, ancestor_col = (
                    self._id_pos_stack[-1] if self._id_pos_stack else (1, 1)
                )
                rel_line = line - ancestor_line
                rel_col = col - ancestor_col
                markup["context_hint"] = f"{self.filename}+{path}:{rel_line}-{rel_col}"
            self._id_pushed_stack.append(False)

        self.append_markup(markup)

    def handle_endtag(self, tag):
        try:
            popped = self.tag_path.pop()
        except IndexError:
            raise ParseError(
                f"Mismatched tags: no more tags: line {self.getpos()[0]}"
            ) from None
        if popped != tag and popped in self.EMPTY_HTML_ELEMENTS:
            popped = self.tag_path.pop()
        if popped != tag:
            raise ParseError(
                "Mismatched closing tag: "
                f"expected '{popped}' got '{tag}' at line {self.getpos()[0]}"
            )

        self.append_markup({"type": "endtag", "html_content": f"</{tag}>"})

        # Check if this closing tag corresponds to an ignored tag
        # We match from the end of the stack because tags are properly nested
        if self.ignore_tag_stack and self.ignore_tag_stack[-1] == tag:
            self.ignore_tag_stack.pop()
            self.ignore_depth -= 1

        if tag in self.TRANSLATABLE_ELEMENTS and not self.is_extraction_ignored():
            self.end_translation_unit()
            if any(t in self.TRANSLATABLE_ELEMENTS for t in self.tag_path):
                self.begin_translation_unit()

        # Pop ancestor id if closing the element that defined it
        if self._id_pushed_stack:
            pushed = self._id_pushed_stack.pop()
            if pushed and self.ancestor_id_stack:
                self.ancestor_id_stack.pop()
                if self._id_depth_stack:
                    self._id_depth_stack.pop()
                if self._id_pos_stack:
                    self._id_pos_stack.pop()
                if self._ancestor_id_label_stack:
                    self._ancestor_id_label_stack.pop()

    def handle_startendtag(self, tag, attrs):
        self.auto_close_empty_element()
        self.tag_path.append(tag)

        # Check for data-translate-ignore attribute
        attrs_dict = dict(attrs)
        has_ignore_attr = "data-translate-ignore" in attrs_dict

        # For self-closing tags with ignore attribute, temporarily set ignore state
        if has_ignore_attr:
            self.ignore_depth += 1

        if tag in self.TRANSLATABLE_ELEMENTS and not self.is_extraction_ignored():
            self.begin_translation_unit()

        translated_attrs = self.translate_attributes(tag, attrs)
        markup = {
            "type": "startendtag",
            "html_content": self.create_start_tag(tag, translated_attrs, startend=True),
            "untranslated_html": self.create_start_tag(tag, attrs, startend=True),
            "attribute_tus": self.extract_translatable_attributes(tag, attrs),
        }

        # Extract data-translate-comment attribute
        if "data-translate-comment" in attrs_dict:
            markup["translate_comment"] = attrs_dict["data-translate-comment"]

        # Extract data-translate-context attribute
        if "data-translate-context" in attrs_dict:
            context_raw = attrs_dict.get("data-translate-context") or ""
            context_value = self.WHITESPACE_RE.sub(" ", context_raw).strip()
            if context_value:
                markup["translate_context"] = context_value
                self._id_pushed_stack.append(False)
        elif "id" in attrs_dict:
            id_raw = attrs_dict.get("id") or ""
            id_value = self.WHITESPACE_RE.sub(" ", id_raw).strip()
            if id_value:
                id_line, id_col = self.getpos()[0], self.getpos()[1] + 1
                if id_value in getattr(self, "_id_seen", set()):
                    id_label = f"{id_value}:{id_line}-{id_col}"
                    markup["context_hint"] = (
                        f"{self.filename}+{id_value}:{id_line}-{id_col}"
                    )
                else:
                    id_label = id_value
                    markup["context_hint"] = f"{self.filename}:{id_value}"
                    self._id_seen.add(id_value)
                # temporary ancestor; will be popped below
                self.ancestor_id_stack.append(id_value)
                self._ancestor_id_label_stack.append(id_label)
                self._id_pushed_stack.append(True)
                self._id_depth_stack.append(len(self.tag_path) - 1)
                self._id_pos_stack.append((id_line, id_col))
        else:
            # No explicit context and no own id; if within ancestor with id, use path as hint
            ancestor_id = self.ancestor_id_stack[-1] if self.ancestor_id_stack else None
            if ancestor_id:
                line, col = self.getpos()[0], self.getpos()[1] + 1
                id_depth = self._id_depth_stack[-1] if self._id_depth_stack else -1
                rel_tags = self.tag_path[id_depth + 1 :]
                ancestor_label = (
                    self._ancestor_id_label_stack[-1]
                    if self._ancestor_id_label_stack
                    else ancestor_id
                )
                path = (
                    ".".join([ancestor_label, *rel_tags])
                    if rel_tags
                    else ancestor_label
                )
                ancestor_line, ancestor_col = (
                    self._id_pos_stack[-1] if self._id_pos_stack else (1, 1)
                )
                rel_line = line - ancestor_line
                rel_col = col - ancestor_col
                markup["context_hint"] = f"{self.filename}+{path}:{rel_line}-{rel_col}"
            self._id_pushed_stack.append(False)

        self.append_markup(markup)

        if tag in self.TRANSLATABLE_ELEMENTS and not self.is_extraction_ignored():
            self.end_translation_unit()
            if any(t in self.TRANSLATABLE_ELEMENTS for t in self.tag_path):
                self.begin_translation_unit()

        # Restore ignore state if we set it
        if has_ignore_attr:
            self.ignore_depth -= 1

        self.tag_path.pop()
        # For startend, if we pushed an id, pop it now
        if self._id_pushed_stack:
            pushed = self._id_pushed_stack.pop()
            if pushed and self.ancestor_id_stack:
                self.ancestor_id_stack.pop()
                if self._id_depth_stack:
                    self._id_depth_stack.pop()
                if self._id_pos_stack:
                    self._id_pos_stack.pop()
                if self._ancestor_id_label_stack:
                    self._ancestor_id_label_stack.pop()

    def _register_unit_for_disambiguation(self, unit, source, context_hint):
        bucket = self._units_by_source.setdefault(source, [])
        bucket.append((unit, context_hint))
        if len(bucket) == 2:
            for u, hint in bucket:
                if hint and not u.getcontext():
                    u.setcontext(hint)
        elif len(bucket) > 2 and context_hint and not unit.getcontext():
            unit.setcontext(context_hint)

    def handle_data(self, data):
        self.auto_close_empty_element()
        self.append_markup({"type": "data", "html_content": data})

    def handle_charref(self, name):
        """Handle entries in the form &#NNNN; e.g. &#8417;."""
        if name.lower().startswith("x"):
            self.handle_data(chr(int(name[1:], 16)))
        else:
            self.handle_data(chr(int(name)))

    def handle_entityref(self, name):
        """Handle named entities of the form &aaaa; e.g. &rsquo;."""
        converted = html5.get(f"{name};")
        if name in {"gt", "lt", "amp"} or not converted:
            self.handle_data(f"&{name};")
        else:
            self.handle_data(converted)

    def handle_comment(self, data):
        self.auto_close_empty_element()

        # Check for translate:off and translate:on directives
        stripped_data = data.strip()
        if stripped_data == "translate:off":
            self.comment_ignore = True
        elif stripped_data == "translate:on":
            self.comment_ignore = False

        self.append_markup(
            {"type": "comment", "html_content": f"<!--{data}-->", "note": data}
        )

    def handle_decl(self, decl):
        self.auto_close_empty_element()
        self.append_markup({"type": "decl", "html_content": f"<!{decl}>"})

    def handle_pi(self, data):
        self.auto_close_empty_element()
        self.append_markup({"type": "pi", "html_content": f"<?{data}?>"})

    def unknown_decl(self, data):
        self.auto_close_empty_element()
        self.append_markup({"type": "cdecl", "html_content": f"<![{data}]>"})


class POHTMLParser(htmlfile):
    pass
