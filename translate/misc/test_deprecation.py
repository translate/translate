# -*- coding: utf-8 -*-

from pytest import deprecated_call, raises

from translate.misc.deprecation import deprecated


class TestDeprecation(object):

    # Deprecated on 2.x.x
    @deprecated("Use XXX instead")
    def deprecated_helper(self):
        pass

    def active_helper(self):
        pass

    def test_deprecated_decorator(self):
        deprecated_call(self.deprecated_helper)

        with raises(AssertionError):
            deprecated_call(self.active_helper)
