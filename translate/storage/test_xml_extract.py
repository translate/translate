#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO

import lxml.etree as etree

from translate.storage import factory

import xml_extract
import odf_shared

odf_file = """<?xml version="1.0" encoding="utf-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
xmlns:math="http://www.w3.org/1998/Math/MathML"
xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
xmlns:ooo="http://openoffice.org/2004/office"
xmlns:ooow="http://openoffice.org/2004/writer"
xmlns:oooc="http://openoffice.org/2004/calc"
xmlns:dom="http://www.w3.org/2001/xml-events"
xmlns:xforms="http://www.w3.org/2002/xforms"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:field="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:field:1.0"
office:version="1.1">
<office:scripts />
<office:font-face-decls>
<style:font-face style:name="Nimbus Roman No9 L"
svg:font-family="'Nimbus Roman No9 L'"
style:font-family-generic="roman" style:font-pitch="variable" />
<style:font-face style:name="Nimbus Sans L"
svg:font-family="'Nimbus Sans L'" style:font-family-generic="swiss"
style:font-pitch="variable" />
<style:font-face style:name="DejaVu Sans"
svg:font-family="'DejaVu Sans'" style:font-family-generic="system"
style:font-pitch="variable" />
</office:font-face-decls>
<office:automatic-styles>
<style:style style:name="Tabel1" style:family="table">
<style:table-properties style:width="16.999cm"
table:align="margins" />
</style:style>
<style:style style:name="Tabel1.A" style:family="table-column">
<style:table-column-properties style:column-width="8.5cm"
style:rel-column-width="32767*" />
</style:style>
<style:style style:name="Tabel1.A1" style:family="table-cell">
<style:table-cell-properties fo:padding="0.097cm"
fo:border-left="0.002cm solid #000000" fo:border-right="none"
fo:border-top="0.002cm solid #000000"
fo:border-bottom="0.002cm solid #000000" />
</style:style>
<style:style style:name="Tabel1.B1" style:family="table-cell">
<style:table-cell-properties fo:padding="0.097cm"
fo:border="0.002cm solid #000000" />
</style:style>
<style:style style:name="Tabel1.A2" style:family="table-cell">
<style:table-cell-properties fo:padding="0.097cm"
fo:border-left="0.002cm solid #000000" fo:border-right="none"
fo:border-top="none" fo:border-bottom="0.002cm solid #000000" />
</style:style>
<style:style style:name="Tabel1.B2" style:family="table-cell">
<style:table-cell-properties fo:padding="0.097cm"
fo:border-left="0.002cm solid #000000"
fo:border-right="0.002cm solid #000000" fo:border-top="none"
fo:border-bottom="0.002cm solid #000000" />
</style:style>
<style:style style:name="fr1" style:family="graphic"
style:parent-style-name="Frame">
<style:graphic-properties fo:margin-left="0cm"
fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm"
style:wrap="dynamic" style:number-wrapped-paragraphs="no-limit"
style:vertical-pos="top" style:vertical-rel="paragraph"
style:horizontal-pos="center" style:horizontal-rel="paragraph"
fo:padding="0cm" fo:border="none" />
</style:style>
<style:style style:name="fr2" style:family="graphic"
style:parent-style-name="Graphics">
<style:graphic-properties fo:margin-left="0cm"
fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm"
style:run-through="foreground" style:wrap="none"
style:vertical-pos="from-top"
style:vertical-rel="paragraph-content"
style:horizontal-pos="from-left"
style:horizontal-rel="paragraph-content" fo:padding="0cm"
fo:border="none" style:shadow="none" style:mirror="none"
fo:clip="rect(0cm 0cm 0cm 0cm)" draw:luminance="0%"
draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%"
draw:gamma="100%" draw:color-inversion="false"
draw:image-opacity="100%" draw:color-mode="standard" />
</style:style>
</office:automatic-styles>
<office:body>
<office:text>
<text:sequence-decls>
<text:sequence-decl text:display-outline-level="0"
text:name="Illustration" />
<text:sequence-decl text:display-outline-level="0"
text:name="Table" />
<text:sequence-decl text:display-outline-level="0"
text:name="Text" />
<text:sequence-decl text:display-outline-level="0"
text:name="Drawing" />
</text:sequence-decls>
<text:p text:style-name="Standard">First. This should
<text:note text:id="ftn0" text:note-class="footnote">
<text:note-citation>1</text:note-citation>
<text:note-body>
<text:p text:style-name="Footnote">Footnote 1</text:p>
</text:note-body>
</text:note>not be segmented. Even with etc. and so.</text:p>
<text:p text:style-name="Standard">Second</text:p>
<text:p text:style-name="Standard">Third</text:p>
<text:p text:style-name="Standard" />
<table:table table:name="Tabel1" table:style-name="Tabel1">
<table:table-column table:style-name="Tabel1.A"
table:number-columns-repeated="2" />
<table:table-row>
<table:table-cell table:style-name="Tabel1.A1"
office:value-type="string">
<text:p text:style-name="Table_20_Contents">cell 1</text:p>
</table:table-cell>
<table:table-cell table:style-name="Tabel1.B1"
office:value-type="string">
<text:p text:style-name="Table_20_Contents">cell 2</text:p>
</table:table-cell>
</table:table-row>
<table:table-row>
<table:table-cell table:style-name="Tabel1.A2"
office:value-type="string">
<text:p text:style-name="Table_20_Contents">cell 3
<text:note text:id="ftn1" text:note-class="footnote">
<text:note-citation>2</text:note-citation>
<text:note-body>
<text:p text:style-name="Footnote">Footnote 2</text:p>
</text:note-body>
</text:note></text:p>
</table:table-cell>
<table:table-cell table:style-name="Tabel1.B2"
office:value-type="string">
<text:p text:style-name="Table_20_Contents">cell 4</text:p>
</table:table-cell>
</table:table-row>
</table:table>
<text:p text:style-name="Standard" />
<text:h text:style-name="Heading_20_1" text:outline-level="1">
Header 1</text:h>
<text:p text:style-name="Text_20_body">
<draw:frame draw:style-name="fr1" draw:name="Raam1"
text:anchor-type="paragraph" svg:width="6.216cm" draw:z-index="0">
<draw:text-box fo:min-height="6.045cm">
<text:p text:style-name="Illustration">
<draw:frame draw:style-name="fr2" draw:name="grafika1"
text:anchor-type="paragraph" svg:x="0.004cm" svg:y="0.002cm"
svg:width="6.216cm" style:rel-width="100%" svg:height="6.045cm"
style:rel-height="scale" draw:z-index="1">
<draw:image xlink:href="Pictures/1000020100000400000003E424286D10.png"
xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad" />
</draw:frame>Illustrasie 
<text:sequence text:ref-name="refIllustration0"
text:name="Illustration" text:formula="ooow:Illustration+1"
style:num-format="1">1</text:sequence>: Pic 1</text:p>
</draw:text-box>
</draw:frame>
</text:p>
</office:text>
</office:body>
</office:document-content>
"""

import re

placeable_pattern = re.compile(u'\[\[\[\w+\]\]\]')

def replace_dom_text(dom_node, unit):
    """Use the unit's target (or source in the case where there is no translation)
    to update the text in the dom_node and at the tails of its children."""
    translation = unicode(unit.target or unit.source)
    # This will alter be used to swap around placeables if their positions are changed
    # Search for all the placeables in 'translation'
    _placeable_tokens = placeable_pattern.findall(translation)
    # Split 'translation' into the different chunks of text which
    # run between the placeables.
    non_placeable_chunks = placeable_pattern.split(translation)
    dom_node.text = non_placeable_chunks[0]
    # Assign everything after the first non_placeable to the
    # tails of the child XML nodes (since this is where such text
    # appears).
    for chunk, child in zip(non_placeable_chunks[1:], dom_node):
        child.tail = chunk

class TestXMLExtract:
    def test_basic(self):
        tree = etree.parse(cStringIO.StringIO(odf_file))
        result = xml_extract.apply(tree.getroot(), xml_extract.ParseState(odf_shared.odf_namespace_table, odf_shared.odf_placables_table))
        return result

    def test_extract(self):
        #store = factory.classes['xlf']()
        store = factory.classes['po']()
        xml_extract.build_store(cStringIO.StringIO(odf_file), store)
        print store

    def test_roundtrip(self):      
        def first_child(unit_node):
            return unit_node.children.values()[0]

        store = factory.classes['xlf']()
        tree = xml_extract.build_store(cStringIO.StringIO(odf_file), store)
        root = tree.getroot()
        unit_tree = first_child(xml_extract.build_unit_tree(store))
        xml_extract.apply_translations(root, unit_tree, replace_dom_text)
        print etree.tostring(tree)

t = TestXMLExtract()
t.test_roundtrip()
