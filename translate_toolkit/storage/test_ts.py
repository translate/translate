from translate_toolkit.storage import ts


class TestTS:
    @staticmethod
    def test_construct():
        tsfile = ts.QtTsParser()
        tsfile.addtranslation("ryan", "Bread", "Brood", "Wit", createifmissing=True)
