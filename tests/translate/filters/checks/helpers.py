"""Shared assertion helpers for the checker tests."""

from translate.filters import checks
from translate.lang import data


def strprep(str1, str2, message=None):
    return (
        data.normalize(str1),
        data.normalize(str2),
        data.normalize(message),
    )


def check_category(filterfunction):
    """Checks whether ``filterfunction`` has defined a category or not."""
    return filterfunction.__name__ in filterfunction.__self__.categories


def passes(filterfunction, str1, str2):
    """Returns whether the given strings pass on the given test, handling FilterFailures."""
    str1, str2, _no_message = strprep(str1, str2)
    try:
        filterresult = filterfunction(str1, str2)
    except checks.FilterFailure:
        filterresult = False

    return filterresult and check_category(filterfunction)


def fails(filterfunction, str1, str2, message=None) -> bool:
    """Returns whether the given strings fail on the given test, handling only FilterFailures."""
    str1, str2, message = strprep(str1, str2, message)
    try:
        filterresult = filterfunction(str1, str2)
    except checks.SeriousFilterFailure:
        filterresult = True
    except checks.FilterFailure as e:
        if message:
            exc_message = e.messages[0]
            filterresult = exc_message != message
            print(exc_message.encode("utf-8"))
        else:
            filterresult = False

    filterresult = filterresult and check_category(filterfunction)

    return not filterresult


def fails_serious(filterfunction, str1, str2, message=None) -> bool:
    """Returns whether the given strings fail on the given test, handling only SeriousFilterFailures."""
    str1, str2, message = strprep(str1, str2, message)
    try:
        filterresult = filterfunction(str1, str2)
    except checks.SeriousFilterFailure as e:
        if message:
            exc_message = e.messages[0]
            filterresult = exc_message != message
            print(exc_message.encode("utf-8"))
        else:
            filterresult = False

    filterresult = filterresult and check_category(filterfunction)

    return not filterresult
