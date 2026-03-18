from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from translate.misc.zipfile_helpers import (
    MAX_ARCHIVE_MEMBER_SIZE,
    MAX_ARCHIVE_TOTAL_SIZE,
)
from translate.storage import odf_io


def test_open_odf_rejects_large_members(tmp_path) -> None:
    archive = tmp_path / "large.odt"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("content.xml", b"A" * (MAX_ARCHIVE_MEMBER_SIZE + 1))
        zip_file.writestr("meta.xml", b"B")
        zip_file.writestr("styles.xml", b"C")

    with pytest.raises(ValueError, match="too large after decompression"):
        odf_io.open_odf(archive)


def test_copy_odf_rejects_large_members(tmp_path) -> None:
    archive = tmp_path / "large-template.odt"
    output = tmp_path / "out.odt"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("content.xml", b"A")
        zip_file.writestr("meta.xml", b"B")
        zip_file.writestr("styles.xml", b"C")
        zip_file.writestr("other.bin", b"D" * (MAX_ARCHIVE_MEMBER_SIZE + 1))

    with (
        ZipFile(archive, "r") as input_zip,
        ZipFile(output, "w") as output_zip,
        pytest.raises(ValueError, match="too large after decompression"),
    ):
        odf_io.copy_odf(input_zip, output_zip, {"content.xml"})


def test_copy_odf_allows_large_total_size_when_members_are_bounded(tmp_path) -> None:
    archive = tmp_path / "large-total-template.odt"
    output = tmp_path / "out-large-total.odt"
    member_size = MAX_ARCHIVE_TOTAL_SIZE // 3
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("content.xml", b"A")
        zip_file.writestr("meta.xml", b"B")
        zip_file.writestr("styles.xml", b"C")
        zip_file.writestr("asset-1.bin", b"D" * member_size)
        zip_file.writestr("asset-2.bin", b"E" * member_size)
        zip_file.writestr("asset-3.bin", b"F" * member_size)
        zip_file.writestr("asset-4.bin", b"G" * member_size)

    with ZipFile(archive, "r") as input_zip, ZipFile(output, "w") as output_zip:
        odf_io.copy_odf(input_zip, output_zip, {"content.xml"})

    with ZipFile(output, "r") as output_zip:
        assert output_zip.read("asset-4.bin") == b"G" * member_size
