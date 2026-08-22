#
# Copyright 2012 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""Decorators to categorize pofilter checks."""

from collections.abc import Callable
from functools import wraps
from typing import Protocol, TypeVar, cast

R_co = TypeVar("R_co", covariant=True)


#: Quality checks' failure categories
class Category:
    CRITICAL = 100
    FUNCTIONAL = 60
    COSMETIC = 30
    EXTRACTION = 10
    NO_CATEGORY = 0


class Categorizable(Protocol):
    """The part of a checker that the decorators below record categories in."""

    categories: dict[str, int]


class BoundCheckFunction(Protocol[R_co]):
    """A :class:`CheckFunction` accessed on a checker instance."""

    #: Short description of the check, taken from its docstring
    title: str
    #: Name of the wrapped check, copied over by :func:`functools.wraps`
    __name__: str
    #: The checker the check is bound to
    __self__: Categorizable

    def __call__(self, *args, **kwargs) -> R_co: ...


class UndecoratedCheck(Protocol[R_co]):
    """A check method before one of the category decorators below is applied."""

    #: Name of the check, used as the key to record its category under
    __name__: str

    def __call__(self, *args, **kwargs) -> R_co: ...


class CheckFunction(Protocol[R_co]):
    """A check function as returned by the decorators below."""

    #: Short description of the check, taken from its docstring
    title: str
    #: Name of the wrapped check, copied over by :func:`functools.wraps`
    __name__: str

    def __call__(self, *args, **kwargs) -> R_co: ...

    def __get__(
        self, instance: Categorizable, owner: type | None = None
    ) -> BoundCheckFunction[R_co]:
        """Checks are methods, so looking one up on a checker binds it."""


def annotate_check(checkfunc: Callable[..., R_co]) -> CheckFunction[R_co]:
    """
    Annotate check function with title attribute.

    This is generated from the first list of docstring removing any
    extra whitespace caused by indentation.
    """
    check = cast("CheckFunction[R_co]", checkfunc)
    docstring = (checkfunc.__doc__ or "").strip().split("\n\n")[0]
    check.title = " ".join(docstring.split())

    return check


def critical(f: UndecoratedCheck[R_co]) -> CheckFunction[R_co]:
    @wraps(f)
    def critical_f(self: Categorizable, *args, **kwargs) -> R_co:
        if f.__name__ not in self.categories:
            self.categories[f.__name__] = Category.CRITICAL

        return f(self, *args, **kwargs)

    return annotate_check(critical_f)


def functional(f: UndecoratedCheck[R_co]) -> CheckFunction[R_co]:
    @wraps(f)
    def functional_f(self: Categorizable, *args, **kwargs) -> R_co:
        if f.__name__ not in self.categories:
            self.categories[f.__name__] = Category.FUNCTIONAL

        return f(self, *args, **kwargs)

    return annotate_check(functional_f)


def cosmetic(f: UndecoratedCheck[R_co]) -> CheckFunction[R_co]:
    @wraps(f)
    def cosmetic_f(self: Categorizable, *args, **kwargs) -> R_co:
        if f.__name__ not in self.categories:
            self.categories[f.__name__] = Category.COSMETIC

        return f(self, *args, **kwargs)

    return annotate_check(cosmetic_f)


def extraction(f: UndecoratedCheck[R_co]) -> CheckFunction[R_co]:
    @wraps(f)
    def extraction_f(self: Categorizable, *args, **kwargs) -> R_co:
        if f.__name__ not in self.categories:
            self.categories[f.__name__] = Category.EXTRACTION

        return f(self, *args, **kwargs)

    return annotate_check(extraction_f)
