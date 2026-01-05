from pytest import deprecated_call, mark

from translate.misc.deprecation import deprecated


class TestDeprecation:
    # Deprecated on 2.x.x
    @deprecated("Use XXX instead")
    def deprecated_helper(self) -> None:
        pass

    def active_helper(self) -> None:
        pass

    def test_deprecated_decorator(self) -> None:
        with deprecated_call():
            self.deprecated_helper()

    @mark.filterwarnings("error")
    def test_no_deprecated_decorator(self) -> None:
        self.active_helper()
