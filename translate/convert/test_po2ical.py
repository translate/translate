from io import BytesIO

import pytest

from translate.convert import po2ical, test_convert


class TestPO2Ical:
    ConverterClass = po2ical.po2ical

    def _convert(
        self,
        input_string,
        template_string=None,
        include_fuzzy=False,
        output_threshold=None,
        success_expected=True,
    ):
        """Helper that converts to target format without using files."""
        input_file = BytesIO(input_string.encode())
        output_file = BytesIO()
        template_file = None
        if template_string:
            template_file = BytesIO(template_string.encode())
        expected_result = 1 if success_expected else 0
        converter = self.ConverterClass(
            input_file, output_file, template_file, include_fuzzy, output_threshold
        )
        assert converter.run() == expected_result
        return None, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty_file(self):
        """Check that an empty PO converts to valid iCalendar."""
        input_string = ""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Value"
        expected_output = icalendar_boilerplate % "Value"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_summary(self):
        """Check that a simple PO converts valid iCalendar SUMMARY."""
        input_string = """
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr "Waarde"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Value"
        expected_output = icalendar_boilerplate % "Waarde"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_description(self):
        """Check that a simple PO converts valid iCalendar DESCRIPTION."""
        input_string = """
#: [uid1@example.com]DESCRIPTION
msgid "My description"
msgstr "A miña descrición"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DESCRIPTION:%s
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "My description"
        expected_output = icalendar_boilerplate % "A miña descrición"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_location(self):
        """Check that a simple PO converts valid iCalendar LOCATION."""
        input_string = """
#: [uid1@example.com]LOCATION
msgid "The location"
msgstr "O lugar"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
LOCATION:%s
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "The location"
        expected_output = icalendar_boilerplate % "O lugar"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_comment(self):
        """Check that a simple PO converts valid iCalendar COMMENT."""
        input_string = """
#: [uid1@example.com]COMMENT
msgid "Some comment"
msgstr "Comentarios ao chou"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
COMMENT:%s
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Some comment"
        expected_output = icalendar_boilerplate % "Comentarios ao chou"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_complex_icalendar(self):
        """Check that a PO converts valid iCalendar."""
        input_string = """
#: [uid1@example.com]SUMMARY
msgid "My summary"
msgstr "Resumo"

#: [uid1@example.com]DESCRIPTION
msgid "My description"
msgstr "A miña descrición"

#: [uid1@example.com]LOCATION
msgid "The location"
msgstr "O lugar"

#: [uid1@example.com]COMMENT
msgid "Some comment"
msgstr "Comentarios ao chou"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
COMMENT:%s
DESCRIPTION:%s
DTSTAMP:19970714T170000Z
LOCATION:%s
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:%s
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % (
            "Some comment",
            "My description",
            "The location",
            "My summary",
        )
        expected_output = icalendar_boilerplate % (
            "Comentarios ao chou",
            "A miña descrición",
            "O lugar",
            "Resumo",
        )
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_convert_skip_fuzzy(self):
        """Check that by default fuzzy units are converted with source text."""
        input_string = """
#, fuzzy
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr "Waarde"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Value"
        expected_output = icalendar_boilerplate % "Value"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_convert_include_fuzzy(self):
        """Check fuzzy units are converted with target text if specified."""
        input_string = """
#, fuzzy
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr "Waarde"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Value"
        expected_output = icalendar_boilerplate % "Waarde"
        assert expected_output == self._convert_to_string(
            input_string, template_string, include_fuzzy=True
        )

    def test_no_template(self):
        """Check that a template is required."""
        with pytest.raises(ValueError):
            self._convert_to_string("")

    def test_template_location_not_in_source_file(self):
        """Check conversion when template unit is not in source file."""
        input_string = """
#: [NOT_IN_TEMPLATE]SUMMARY
msgid "Value"
msgstr "Waarde"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Random"
        expected_output = icalendar_boilerplate % "Random"
        assert expected_output == self._convert_to_string(input_string, template_string)

    def test_convert_completion_below_threshold(self):
        """Check no conversion if input completion is below threshold."""
        input_string = """
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr ""
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Value"
        expected_output = ""
        # Input completion is 0% so with a 70% threshold it should not output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70, success_expected=False
        )
        assert output == expected_output

    def test_convert_completion_above_threshold(self):
        """Check there is conversion if input completion is above threshold."""
        input_string = """
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr "Waarde"
"""
        icalendar_boilerplate = """BEGIN:VCALENDAR
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
""".replace(
            "\n", "\r\n"
        )
        template_string = icalendar_boilerplate % "Value"
        expected_output = icalendar_boilerplate % "Waarde"
        # Input completion is 100% so with a 70% threshold it should output.
        output = self._convert_to_string(
            input_string, template_string, output_threshold=70
        )
        assert output == expected_output


class TestPO2IcalCommand(test_convert.TestConvertCommand, TestPO2Ical):
    """Tests running actual po2ical commands on files"""

    convertmodule = po2ical
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]
