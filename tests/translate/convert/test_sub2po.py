from io import BytesIO

from translate.convert import sub2po
from translate.storage import po, subtitles

from . import test_convert


def test_input_and_template_encoding(monkeypatch) -> None:
    """Allow input and template subtitle files to use different encodings."""
    input_file = BytesIO(
        "1\n00:00:00,000 --> 00:00:01,000\nCafé\n\n".encode("iso-8859-1")
    )
    template_file = BytesIO(
        "1\n00:00:00,000 --> 00:00:01,000\nSource — UTF-8\n\n".encode()
    )
    output_file = BytesIO()
    monkeypatch.setattr(subtitles, "detect", lambda _filename: "utf-8")

    assert (
        sub2po.convertsub(
            input_file,
            output_file,
            template_file,
            encoding="iso-8859-1",
            template_encoding="utf-8",
        )
        == 1
    )

    result = po.pofile(BytesIO(output_file.getvalue()))
    unit = result.findunit("Source — UTF-8")
    assert unit is not None
    assert unit.target == "Café"


class TestSub2POCommand(test_convert.TestConvertCommand):
    """Tests running actual sub2po commands on files."""

    convertmodule = sub2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-P, --pot",
        "--encoding=ENCODING",
        "--encoding-template=ENCODING",
        "--duplicates=DUPLICATESTYLE",
    ]
