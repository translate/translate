from translate.filters import autocorrect


class TestAutocorrect:
    @staticmethod
    def correct(msgid, msgstr, expected):
        """helper to run correct function from autocorrect module"""
        corrected = autocorrect.correct(msgid, msgstr)
        print(repr(msgid))
        print(repr(msgstr))
        print(msgid.encode("utf-8"))
        print(msgstr.encode("utf-8"))
        print((corrected or "").encode("utf-8"))
        assert corrected == expected

    def test_empty_target(self):
        """test that we do nothing with an empty target"""
        self.correct("String...", "", None)

    def test_correct_ellipsis(self):
        """test that we convert single … or ... to match source and target"""
        self.correct("String...", "Translated…", "Translated...")
        self.correct("String…", "Translated...", "Translated…")

    def test_correct_spacestart_spaceend(self):
        """test that we can correct leading and trailing space errors"""
        self.correct("Simple string", "Dimpled ring  ", "Dimpled ring")
        self.correct("Simple string", "  Dimpled ring", "Dimpled ring")
        self.correct("  Simple string", "Dimpled ring", "  Dimpled ring")
        self.correct("Simple string  ", "Dimpled ring", "Dimpled ring  ")

    def test_correct_start_capitals(self):
        """test that we can correct the starting capital"""
        self.correct("Simple string", "dimpled ring", "Dimpled ring")
        self.correct("simple string", "Dimpled ring", "dimpled ring")

    def test_correct_end_punc(self):
        """test that we can correct end punctuation"""
        self.correct("Simple string:", "Dimpled ring", "Dimpled ring:")
        # self.correct("Simple string: ", "Dimpled ring", "Dimpled ring: ")
        self.correct("Simple string.", "Dimpled ring", "Dimpled ring.")
        # self.correct("Simple string. ", "Dimpled ring", "Dimpled ring. ")
        self.correct("Simple string?", "Dimpled ring", "Dimpled ring?")

    def test_correct_combinations(self):
        """test that we can correct combinations of failures"""
        self.correct("Simple string:", "Dimpled ring ", "Dimpled ring:")
        self.correct("simple string ", "Dimpled ring", "dimpled ring ")
        self.correct("Simple string...", "dimpled ring..", "Dimpled ring...")
        self.correct("Simple string:", "Dimpled ring ", "Dimpled ring:")

    def test_nothing_to_do(self):
        """test that when nothing changes we return None"""
        self.correct("Some text", "A translation", None)
