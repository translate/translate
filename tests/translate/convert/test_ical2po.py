from io import BytesIO

import pytest

from translate.convert import ical2po, test_convert


class TestIcal2PO:
    ConverterClass = ical2po.ical2po

    def _convert(
        self,
        input_string,
        template_string=None,
        blank_msgstr=False,
        duplicate_style="msgctxt",
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
            input_file, output_file, template_file, blank_msgstr, duplicate_style
        )
        assert converter.run() == expected_result
        return converter.target_store, output_file

    def _convert_to_string(self, *args, **kwargs):
        """Helper that converts to target format string without using files."""
        return self._convert(*args, **kwargs)[1].getvalue().decode("utf-8")

    def test_convert_empty_file(self):
        """Check converting empty iCalendar returns no output."""
        with pytest.raises(StopIteration):
            self._convert_to_string("", success_expected=False)

    def test_no_translations(self):
        """Check that iCalendar with no translations returns correct result."""
        input_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        output = self._convert_to_string(input_string, success_expected=False)
        assert output == ""

    def test_summary(self):
        """Check that iCalendar SUMMARY converts valid PO output."""
        input_string = """
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
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_description(self):
        """Check that iCalendar DESCRIPTION converts valid PO output."""
        input_string = """
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
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]DESCRIPTION
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_location(self):
        """Check that iCalendar LOCATION converts valid PO output."""
        input_string = """
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
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]LOCATION
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_comment(self):
        """Check that iCalendar COMMENT converts valid PO output."""
        input_string = """
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
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]COMMENT
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_no_template_duplicate_style(self):
        """Check that iCalendar extracts conforming duplicate style."""
        input_string = """
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
BEGIN:VEVENT
UID:uid2@example.com
DTSTART:19970715T170000Z
DTEND:19970716T035959Z
DTSTAMP:19970715T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Value
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgctxt "[uid1@example.com]SUMMARY"
msgid "Value"
msgstr ""

#. Start date: 1997-07-15 17:00:00+00:00
#: [uid2@example.com]SUMMARY
msgctxt "[uid2@example.com]SUMMARY"
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string)
        assert expected_output in output
        assert "extracted from " in output

        output = self._convert_to_string(input_string, duplicate_style="msgctxt")
        assert expected_output in output
        assert "extracted from " in output

        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#. Start date: 1997-07-15 17:00:00+00:00
#: [uid1@example.com]SUMMARY
#: [uid2@example.com]SUMMARY
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string, duplicate_style="merge")
        assert expected_output in output
        assert "extracted from " in output

    def test_merge(self):
        """Check merging two iCalendar files converts to valid PO output."""
        input_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Valor
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970718T170000Z
DTEND:19970719T035959Z
DTSTAMP:19970718T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Value
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-18 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr "Valor"
"""
        output = self._convert_to_string(input_string, template_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_merge_misaligned_files(self):
        """Check merging two iCalendar files that are not aligned."""
        input_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid3@example.com
DTSTART:19970713T170000Z
DTEND:19970717T035959Z
DTSTAMP:19970713T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Valor
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970718T170000Z
DTEND:19970719T035959Z
DTSTAMP:19970718T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Value
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-18 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(input_string, template_string)
        assert expected_output in output
        assert "extracted from " in output

    def test_merge_blank_msgstr(self):
        """Check merging two iCalendar files converts to valid POT output."""
        input_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Valor
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970718T170000Z
DTEND:19970719T035959Z
DTSTAMP:19970718T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Value
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-18 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgid "Value"
msgstr ""
"""
        output = self._convert_to_string(
            input_string, template_string, blank_msgstr=True
        )
        assert expected_output in output
        assert "extracted from " in output

    def test_merge_duplicate_style(self):
        """Check two iCalendar files convert conforming duplicate style."""
        input_string = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Valor
END:VEVENT
BEGIN:VEVENT
UID:uid2@example.com
DTSTART:19970715T170000Z
DTEND:19970716T035959Z
DTSTAMP:19970715T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Valioso
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        template_string = """
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
BEGIN:VEVENT
UID:uid2@example.com
DTSTART:19970715T170000Z
DTEND:19970716T035959Z
DTSTAMP:19970715T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
SUMMARY:Value
END:VEVENT
END:VCALENDAR
""".replace(
            "\n", "\r\n"
        )
        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#: [uid1@example.com]SUMMARY
msgctxt "[uid1@example.com]SUMMARY"
msgid "Value"
msgstr "Valor"

#. Start date: 1997-07-15 17:00:00+00:00
#: [uid2@example.com]SUMMARY
msgctxt "[uid2@example.com]SUMMARY"
msgid "Value"
msgstr "Valioso"
"""
        output = self._convert_to_string(input_string, template_string)
        assert expected_output in output
        assert "extracted from " in output

        output = self._convert_to_string(
            input_string, template_string, duplicate_style="msgctxt"
        )
        assert expected_output in output
        assert "extracted from " in output

        expected_output = """
#. Start date: 1997-07-14 17:00:00+00:00
#. Start date: 1997-07-15 17:00:00+00:00
#: [uid1@example.com]SUMMARY
#: [uid2@example.com]SUMMARY
#, fuzzy
msgid "Value"
msgstr "Valor"
"""
        output = self._convert_to_string(
            input_string, template_string, duplicate_style="merge"
        )
        assert expected_output in output
        assert "extracted from " in output


class TestIcal2POCommand(test_convert.TestConvertCommand, TestIcal2PO):
    """Tests running actual ical2po commands on files"""

    convertmodule = ical2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
        "--duplicates=DUPLICATESTYLE",
    ]
