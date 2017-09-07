# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from translate.convert import po2ical, test_convert
from translate.misc import wStringIO


class TestPO2Ical(object):

    def format2po_text(self, po_input_source, format_template_source=None,
                       include_fuzzy=False, output_threshold=None):
        """Helper that converts PO source to format output without files."""
        input_file = wStringIO.StringIO(po_input_source)
        output_file = wStringIO.StringIO()
        template_file = None
        if format_template_source:
            template_file = wStringIO.StringIO(format_template_source)
        result = po2ical.convertical(input_file, output_file, template_file,
                                     include_fuzzy, output_threshold)
        assert result == 1
        return output_file.getvalue().decode('utf-8')

    def test_summary(self):
        """Check that a simple PO converts valid iCalendar SUMMARY."""
        input_source = """
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr "Waarde"
"""
        icalendar_boilerplate = '''BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:%s
END:VEVENT
END:VCALENDAR
'''.replace("\n", "\r\n")
        template_source = icalendar_boilerplate % "Value"
        expected_output = icalendar_boilerplate % "Waarde"
        assert expected_output == self.format2po_text(input_source,
                                                      template_source)

    # FIXME we should also test for DESCRIPTION, LOCATION and COMMENT
    # The library handle any special encoding issues, we might want to test
    # those


class TestPO2IcalCommand(test_convert.TestConvertCommand, TestPO2Ical):
    """Tests running actual po2ical commands on files"""
    convertmodule = po2ical
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)
