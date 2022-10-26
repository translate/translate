from translate.convert import po2moz, test_convert


class TestPO2Moz:
    pass


class TestPO2MozCommand(test_convert.TestConvertCommand, TestPO2Moz):
    """Tests running actual po2moz commands on files"""

    convertmodule = po2moz
    defaultoptions = {"progress": "none"}
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-l LOCALE, --locale=LOCALE",
        "--removeuntranslated",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
    ]
