"""Tests for the checks that inspect a whole translation unit."""

from translate.filters import checks
from translate.storage import po, xliff


def test_nplurals() -> None:
    """
    Test that we can find the wrong number of plural forms. Note that this
    test uses a UnitChecker, not a translation checker.
    """
    checker = checks.StandardUnitChecker()
    unit = po.pounit("")

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer", "%d lêers"]
    assert checker.nplurals(unit)

    checker = checks.StandardUnitChecker(checks.CheckerConfig(targetlanguage="af"))
    unit.source = "%d files"
    unit.target = "%d lêer"
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer", "%d lêers"]
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer", "%d lêers", "%d lêeeeers"]
    assert not checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer"]
    assert not checker.nplurals(unit)

    checker = checks.StandardUnitChecker(checks.CheckerConfig(targetlanguage="km"))
    unit.source = "%d files"
    unit.target = "%d ឯកសារ"
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d ឯកសារ"]
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d ឯកសារ", "%d lêers"]
    assert not checker.nplurals(unit)


def test_hassuggestion() -> None:
    """Test that hassuggestion() works."""
    checker = checks.StandardUnitChecker()

    po_store = po.pofile()
    po_store.addsourceunit("koeie")
    assert checker.hassuggestion(po_store.units[-1])

    xliff_store = xliff.xlifffile.parsestring(
        """
<xliff version='1.2'
       xmlns='urn:oasis:names:tc:xliff:document:1.2'>
<file original='hello.txt' source-language='en' target-language='fr' datatype='plaintext'>
<body>
    <trans-unit id='hi'>
        <source>Hello world</source>
        <target>Bonjour le monde</target>
        <alt-trans>
            <target xml:lang='es'>Hola mundo</target>
        </alt-trans>
    </trans-unit>
</body>
</file>
</xliff>
"""
    )
    assert not checker.hassuggestion(xliff_store.units[0])
