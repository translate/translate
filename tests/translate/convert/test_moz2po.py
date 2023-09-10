from translate.convert import moz2po, test_convert


class TestMoz2PO:
    pass


class TestMoz2POCommand(test_convert.TestConvertCommand, TestMoz2PO):
    """Tests running actual moz2po commands on files"""

    convertmodule = moz2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "--duplicates=DUPLICATESTYLE",
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
    ]
