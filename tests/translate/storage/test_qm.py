import struct
from io import BytesIO

import pytest

from translate.storage import factory, qm

from . import test_base


def make_qm(messages: bytes, trailing: bytes = b"") -> bytes:
    """Build a QM file containing one messages section."""
    magic = struct.pack(">4L", *qm.QM_MAGIC_NUMBER)
    return magic + struct.pack(">BL", 0x69, len(messages)) + messages + trailing


def make_length_record(subsection: int, length: int, payload: bytes = b"") -> bytes:
    """Build a message record with a signed length."""
    return bytes([subsection]) + struct.pack(">l", length) + payload


class TestQtUnit(test_base.TestTranslationUnit):
    UnitClass = qm.qmunit


class TestQtFile(test_base.TestTranslationStore):
    StoreClass = qm.qmfile

    def test_parse(self) -> None:
        messages = (
            make_length_record(0x03, -1)
            + make_length_record(0x06, 6, b"source")
            + b"\x01"
        )

        store = self.StoreClass.parsestring(make_qm(messages))

        assert len(store.units) == 1
        assert store.units[0].source == "source"
        assert store.units[0].target == ""

    @pytest.mark.parametrize("subsection", [0x06, 0x07, 0x08])
    def test_negative_byte_string_length(self, subsection: int) -> None:
        messages = make_length_record(subsection, -5, b"abcd")

        with pytest.raises(ValueError, match="length out of range"):
            self.StoreClass.parsestring(make_qm(messages))

    def test_negative_translation_length(self) -> None:
        with pytest.raises(ValueError, match="invalid translation length"):
            self.StoreClass.parsestring(make_qm(make_length_record(0x03, -2)))

    def test_odd_translation_length(self) -> None:
        messages = make_length_record(0x03, 1, b"a")

        with pytest.raises(ValueError, match="invalid translation length"):
            self.StoreClass.parsestring(make_qm(messages))

    @pytest.mark.parametrize("subsection", [0x03, 0x05, 0x06, 0x07, 0x08])
    def test_truncated_message_record(self, subsection: int) -> None:
        messages = bytes([subsection]) + b"\x00\x00\x00"

        with pytest.raises(ValueError, match="message record truncated"):
            self.StoreClass.parsestring(make_qm(messages))

    @pytest.mark.parametrize("subsection", [0x03, 0x06, 0x07, 0x08])
    def test_message_payload_out_of_range(self, subsection: int) -> None:
        messages = make_length_record(subsection, 2)

        with pytest.raises(ValueError, match="length out of range"):
            self.StoreClass.parsestring(make_qm(messages))

    def test_message_payload_cannot_cross_section_boundary(self) -> None:
        messages = make_length_record(0x06, 1)
        trailing_section = struct.pack(">BLB", 0x42, 1, 0)

        with pytest.raises(ValueError, match="source length out of range"):
            self.StoreClass.parsestring(make_qm(messages, trailing_section))

    def test_factory_rejects_negative_length(self) -> None:
        input_file = BytesIO(make_qm(make_length_record(0x06, -5, b"abcd")))
        input_file.name = "evil.qm"

        with pytest.raises(ValueError, match="source length out of range"):
            factory.getobject(input_file)

    def test_save(self) -> None:
        # QM does not implement saving
        with pytest.raises(TypeError):
            self.StoreClass.savefile(self.StoreClass())  # ty:ignore[missing-argument]

    def test_files(self) -> None:
        # QM does not implement saving
        with pytest.raises(TypeError):
            self.StoreClass.savefile(self.StoreClass())  # ty:ignore[missing-argument]

    def test_nonascii(self) -> None:
        # QM does not implement serialising
        with pytest.raises(TypeError):
            self.StoreClass.serialize(self.StoreClass())  # ty:ignore[missing-argument]

    def test_add(self) -> None:
        # QM does not implement serialising
        with pytest.raises(TypeError):
            self.StoreClass.serialize(self.StoreClass())  # ty:ignore[missing-argument]

    def test_remove(self) -> None:
        # QM does not implement serialising
        with pytest.raises(TypeError):
            self.StoreClass.serialize(self.StoreClass())  # ty:ignore[missing-argument]
