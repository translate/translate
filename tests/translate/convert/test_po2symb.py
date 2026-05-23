from types import SimpleNamespace

import pytest

from translate.convert import po2symb


class EndOfFileWriteState:
    current_line = 'rls_string r_title "Old title"\n'

    def read_line(self):
        raise StopIteration


def test_replace_body_item_updates_current_line_before_eof(monkeypatch) -> None:
    """The final body entry is rewritten before EOF is reported to the caller."""
    monkeypatch.setattr(po2symb, "eat_whitespace", lambda ps: None)
    monkeypatch.setattr(po2symb, "skip_no_translate", lambda ps: None)
    state = EndOfFileWriteState()

    with pytest.raises(StopIteration):
        po2symb.replace_body_item(
            state, {"r_title": SimpleNamespace(source="Source", target="New title")}
        )

    assert state.current_line == 'rls_string r_title "New title"\n'
