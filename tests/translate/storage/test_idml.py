from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from translate.misc.zipfile_helpers import (
    MAX_ARCHIVE_MEMBER_SIZE,
    MAX_ARCHIVE_TOTAL_SIZE,
)
from translate.storage import idml


def test_open_idml_rejects_large_members(tmp_path) -> None:
    archive = tmp_path / "large.idml"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr(
            "Stories/Story_u1.xml",
            b"A" * (MAX_ARCHIVE_MEMBER_SIZE + 1),
        )

    with pytest.raises(ValueError, match="too large after decompression"):
        idml.open_idml(archive)


def test_copy_idml_rejects_large_members(tmp_path) -> None:
    archive = tmp_path / "large-template.idml"
    output = tmp_path / "out.idml"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("Stories/Story_u1.xml", b"A")
        zip_file.writestr("Resources/Graphic.ai", b"B" * (MAX_ARCHIVE_MEMBER_SIZE + 1))

    with (
        ZipFile(archive, "r") as input_zip,
        ZipFile(output, "w") as output_zip,
        pytest.raises(ValueError, match="too large after decompression"),
    ):
        idml.copy_idml(input_zip, output_zip, {"Stories/Story_u1.xml"})


def test_copy_idml_allows_large_total_size_when_members_are_bounded(tmp_path) -> None:
    archive = tmp_path / "large-total-template.idml"
    output = tmp_path / "out-large-total.idml"
    member_size = MAX_ARCHIVE_TOTAL_SIZE // 3
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        zip_file.writestr("Stories/Story_u1.xml", b"A")
        zip_file.writestr("Resources/Graphic-1.ai", b"B" * member_size)
        zip_file.writestr("Resources/Graphic-2.ai", b"C" * member_size)
        zip_file.writestr("Resources/Graphic-3.ai", b"D" * member_size)
        zip_file.writestr("Resources/Graphic-4.ai", b"E" * member_size)

    with ZipFile(archive, "r") as input_zip, ZipFile(output, "w") as output_zip:
        idml.copy_idml(input_zip, output_zip, {"Stories/Story_u1.xml"})

    with ZipFile(output, "r") as output_zip:
        assert output_zip.read("Resources/Graphic-4.ai") == b"E" * member_size
