from translate.tools import podebug
from translate.storage import base

class TestPODebug:

    debug = podebug.podebug()

    def test_ignore_gtk(self):
        unit = base.TranslationUnit("default:LTR")
        assert self.debug.ignore_gtk(unit) == True
