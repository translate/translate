from translate.convert import moz2po, test_convert


class TestMoz2PO:
    pass


class TestMoz2POCommand(test_convert.TestConvertCommand, TestMoz2PO):
    """Tests running actual moz2po commands on files"""

    convertmodule = moz2po
    defaultoptions = {"progress": "none"}

    def test_help(self, capsys):
        """tests getting help"""
        options = super().test_help(capsys)
        options = self.help_check(options, "--duplicates=DUPLICATESTYLE")
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(
            options, "-t TEMPLATE, --template=TEMPLATE", last=True
        )
