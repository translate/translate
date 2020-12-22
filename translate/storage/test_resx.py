#
# Copyright 2015 Zuza Software Foundation
# Copyright 2015 Sarah Hale
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

from io import BytesIO

from translate.storage import resx, test_monolingual


class TestRESXUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = resx.RESXUnit


class TestRESXUnitFromParsedString(TestRESXUnit):
    resxsource = XMLskeleton = """<?xml version="1.0" encoding="utf-8"?>
<root>
  <xsd:schema xmlns="" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" id="root">
    <xsd:import namespace="http://www.w3.org/XML/1998/namespace" />
    <xsd:element name="root" msdata:IsDataSet="true">
      <xsd:complexType>
        <xsd:choice maxOccurs="unbounded">
          <xsd:element name="metadata">
            <xsd:complexType>
              <xsd:sequence>
                <xsd:element name="value" type="xsd:string" minOccurs="0" />
              </xsd:sequence>
              <xsd:attribute name="name" use="required" type="xsd:string" />
              <xsd:attribute name="type" type="xsd:string" />
              <xsd:attribute name="mimetype" type="xsd:string" />
              <xsd:attribute ref="xml:space" />
            </xsd:complexType>
          </xsd:element>
          <xsd:element name="assembly">
            <xsd:complexType>
              <xsd:attribute name="alias" type="xsd:string" />
              <xsd:attribute name="name" type="xsd:string" />
            </xsd:complexType>
          </xsd:element>
          <xsd:element name="data">
            <xsd:complexType>
              <xsd:sequence>
                <xsd:element name="value" type="xsd:string" minOccurs="0" msdata:Ordinal="1" />
                <xsd:element name="comment" type="xsd:string" minOccurs="0" msdata:Ordinal="2" />
              </xsd:sequence>
              <xsd:attribute name="name" type="xsd:string" use="required" msdata:Ordinal="1" />
              <xsd:attribute name="type" type="xsd:string" msdata:Ordinal="3" />
              <xsd:attribute name="mimetype" type="xsd:string" msdata:Ordinal="4" />
              <xsd:attribute ref="xml:space" />
            </xsd:complexType>
          </xsd:element>
          <xsd:element name="resheader">
            <xsd:complexType>
              <xsd:sequence>
                <xsd:element name="value" type="xsd:string" minOccurs="0" msdata:Ordinal="1" />
              </xsd:sequence>
              <xsd:attribute name="name" type="xsd:string" use="required" />
            </xsd:complexType>
          </xsd:element>
        </xsd:choice>
      </xsd:complexType>
    </xsd:element>
  </xsd:schema>
  <resheader name="resmimetype">
    <value>text/microsoft-resx</value>
  </resheader>
  <resheader name="version">
    <value>2.0</value>
  </resheader>
  <data name="key" xml:space="preserve">
    <value>Test String</value>
  </data>
  %s
</root>"""

    def setup_method(self, method):
        self.store = resx.RESXFile.parsestring(self.resxsource % "")
        self.unit = self.store.units[0]

    def _assert_store(self, expected_resx):
        output_file = BytesIO()
        self.store.serialize(output_file)
        actual_resx = output_file.getvalue().decode("utf-8")
        assert actual_resx == expected_resx

    def test_newunit(self):
        new_unit = resx.RESXUnit("New translated value")
        new_unit.setid("test")
        self.store.addunit(new_unit)

        expected_resx = (
            self.resxsource
            % """<data name="test" xml:space="preserve">
    <value>New translated value</value>
  </data>"""
        )
        self._assert_store(expected_resx)

    def test_newunit_comment(self):
        new_unit = resx.RESXUnit("New translated value")
        new_unit.setid("test")
        new_unit.addnote("this unit didn't exist before")
        self.store.addunit(new_unit)

        expected_resx = (
            self.resxsource
            % """<data name="test" xml:space="preserve">
    <value>New translated value</value>
    <comment>this unit didn't exist before</comment>
  </data>"""
        )
        self._assert_store(expected_resx)


class TestRESXfile(test_monolingual.TestMonolingualStore):
    StoreClass = resx.RESXFile

    def resxparse(self, resxsource):
        """helper that parses resx source without requiring files"""
        dummyfile = BytesIO(resxsource.encode())
        return self.StoreClass(dummyfile)
