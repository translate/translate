from io import StringIO

import pytest

from translate.storage import ical


@pytest.mark.parametrize("with_unit", [False, True])
def test_serialize_unparsed(with_unit: bool) -> None:
    store = ical.icalfile()
    if with_unit:
        unit = store.addsourceunit("Summary")
        unit.addlocation("[uid1@example.com]SUMMARY")
        unit.target = "Translated summary"

    out = StringIO()
    store.serialize(out)

    assert out.getvalue() == ""


def test_parse_and_serialize_translation() -> None:
    content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Translate Toolkit//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTSTAMP:19970714T170000Z
SUMMARY:Summary
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")
    store = ical.icalfile()
    store.parse(content.encode())

    assert len(store.units) == 1
    unit = store.units[0]
    assert unit.source == "Summary"
    assert unit.getlocations() == ["[uid1@example.com]SUMMARY"]
    unit.target = "Translated summary"

    out = StringIO()
    store.serialize(out)

    assert out.getvalue() == content.replace(
        "SUMMARY:Summary", "SUMMARY:Translated summary"
    )
