# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from translate.convert import ical2po, test_convert
from translate.misc import wStringIO


class TestIcal2PO(object):

    def convert_to_target_text(self, input_source, template_source=None,
                               blank_msgstr=False, duplicate_style="msgctxt"):
        """Helper that converts format input to PO output without files."""
        input_file = wStringIO.StringIO(input_source)
        output_file = wStringIO.StringIO()
        template_file = None
        if template_source:
            template_file = wStringIO.StringIO(template_source)
        result = ical2po.convertical(input_file, output_file, template_file,
                                     blank_msgstr, duplicate_style)
        assert result == 1
        return output_file.getvalue().decode('utf-8')

    def test_convert_empty_file(self):
        """Check converting empty iCalendar returns no output."""
        input_file = wStringIO.StringIO('')
        output_file = wStringIO.StringIO()
        template_file = None
        with pytest.raises(StopIteration):
            ical2po.convertical(input_file, output_file, template_file)

    def test_summary(self):
        """Check that iCalendar SUMMARY converts valid PO output."""
        input_source = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Value
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")
        expected_unit_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr ""
"""
        output = self.convert_to_target_text(input_source)
        assert expected_unit_output in output
        assert "extracted from " in output

    def test_description(self):
        """Check that iCalendar DESCRIPTION converts valid PO output."""
        input_source = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DESCRIPTION:Value
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")
        expected_unit_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]DESCRIPTION
msgid "Value"
msgstr ""
"""
        output = self.convert_to_target_text(input_source)
        assert expected_unit_output in output
        assert "extracted from " in output

    def test_location(self):
        """Check that iCalendar LOCATION converts valid PO output."""
        input_source = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
LOCATION:Value
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")
        expected_unit_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]LOCATION
msgid "Value"
msgstr ""
"""
        output = self.convert_to_target_text(input_source)
        assert expected_unit_output in output
        assert "extracted from " in output

    def test_comment(self):
        """Check that iCalendar COMMENT converts valid PO output."""
        input_source = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
COMMENT:Value
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")
        expected_unit_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]COMMENT
msgid "Value"
msgstr ""
"""
        output = self.convert_to_target_text(input_source)
        assert expected_unit_output in output
        assert "extracted from " in output


class TestIcal2POCommand(test_convert.TestConvertCommand, TestIcal2PO):
    """Tests running actual ical2po commands on files"""
    convertmodule = ical2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
