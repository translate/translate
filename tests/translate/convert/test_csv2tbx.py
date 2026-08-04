from io import BytesIO

import pytest

from translate.convert import csv2tbx
from translate.storage import tbx

from . import test_convert


def test_convertcsv_encoding() -> None:
    """Decode CSV input using the requested encoding."""
    content = "source,target\ntest,zkouška sirén\n".encode("iso-8859-2")
    output = BytesIO()

    assert csv2tbx.convertcsv(BytesIO(content), output, None, charset="iso-8859-2") == 1

    result = tbx.tbxfile(BytesIO(output.getvalue()))
    assert len(result.units) == 1
    assert result.units[0].source == "test"
    assert result.units[0].target == "zkouška sirén"


def test_convertcsv_invalid_encoding() -> None:
    """Do not silently ignore an invalid CSV encoding."""
    with pytest.raises(LookupError):
        csv2tbx.convertcsv(
            BytesIO(b"source,target\ntest,translation\n"),
            BytesIO(),
            None,
            charset="not-a-codec",
        )


class TestCSV2TBXCommand(test_convert.TestConvertCommand):
    """Tests running actual csv2tbx commands on files."""

    convertmodule = csv2tbx
    defaultoptions = {"progress": "none"}

    expected_options = [
        "--encoding=ENCODING, --charset=ENCODING",
        "--columnorder=COLUMNORDER",
    ]
