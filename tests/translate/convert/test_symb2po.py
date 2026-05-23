from translate.convert import symb2po


class EndOfFileReadState:
    current_line = 'rls_string r_title "Hello"\n'

    def read_line(self):
        raise StopIteration


def test_read_body_item_keeps_last_entry_when_reading_past_eof(monkeypatch) -> None:
    """The final body entry is still returned when advancing hits EOF."""
    monkeypatch.setattr(symb2po, "eat_whitespace", lambda ps: None)
    monkeypatch.setattr(symb2po, "skip_no_translate", lambda ps: None)

    unit, has_more = symb2po.read_body_item(EndOfFileReadState())

    assert unit == ("r_title", "Hello")
    assert has_more is False
