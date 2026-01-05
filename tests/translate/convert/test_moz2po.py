from io import BytesIO

from translate.convert import moz2po, prop2po
from translate.storage import properties

from . import test_convert


class TestMoz2PO:
    @staticmethod
    def moz2po(propsource, proptemplate=None):
        """Helper that converts Mozilla .properties source to po source without requiring files."""
        inputfile = BytesIO(propsource.encode())
        inputprop = properties.propfile(inputfile, personality="mozilla")
        convertor = prop2po.prop2po(personality="mozilla")
        if proptemplate:
            templatefile = BytesIO(proptemplate.encode())
            templateprop = properties.propfile(templatefile, personality="mozilla")
            outputpo = convertor.mergestore(templateprop, inputprop)
        else:
            outputpo = convertor.convertstore(inputprop)
        return outputpo

    def test_duplicate_locations(self) -> None:
        """
        Test that duplicate locations in Mozilla properties files don't cause
        AttributeError. This tests the fix for the Lithuanian Firefox recovery issue.
        """
        # Template file with duplicate keys (like in Lithuanian Firefox files)
        templateprop = """css.property.one=First value
css.property.one=Duplicate value
css.property.two=Second value
"""
        # Translation file with duplicate keys
        translatedprop = """css.property.one=Primera valor
css.property.one=Valor duplicado
css.property.two=Segunda valor
"""
        # This should not raise AttributeError: 'NoneType' object has no attribute 'getid'
        pofile = self.moz2po(translatedprop, templateprop)

        # Verify we got results (not testing exact structure, just that it didn't crash)
        assert len(pofile.units) > 1
        # At least one unit should have the location 'css.property.one'
        locations = []
        for unit in pofile.units:
            if not unit.isheader():
                locations.extend(unit.getlocations())
        assert "css.property.one" in locations
        assert "css.property.two" in locations


class TestMoz2POCommand(test_convert.TestConvertCommand, TestMoz2PO):
    """Tests running actual moz2po commands on files."""

    convertmodule = moz2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "--duplicates=DUPLICATESTYLE",
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
    ]
