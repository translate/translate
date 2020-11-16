#
# Copyright 2007-2010 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""This module provides a factory to instantiate language classes."""

import pkgutil
from functools import lru_cache
from importlib import import_module

from translate.lang import common, data


prefix = "code_"


@lru_cache(maxsize=128)
def getlanguage(code):
    """This returns a language class.

    :param code: The ISO 639 language code
    """
    if code:
        code = code.replace("-", "_").replace("@", "_").lower()
    try:
        if code is None:
            raise ImportError("Can't determine language code")
        if code in ("or", "is", "as"):
            internal_code = prefix + code
        else:
            internal_code = code
        module = import_module("translate.lang.%s" % internal_code)
        langclass = getattr(module, internal_code)
        return langclass(code)
    except ImportError:
        simplercode = data.simplercode(code)
        if simplercode:
            relatedlanguage = getlanguage(simplercode)
            if isinstance(relatedlanguage, common.Common):
                relatedlanguage = relatedlanguage.__class__(code)
            return relatedlanguage
        else:
            return common.Common(code)


def get_all_languages():
    """Return all language classes."""
    import translate.lang as package

    is_language_module = lambda x: not (
        x.startswith("test_")
        or x in ("common", "data", "factory", "identify", "ngram", "poedit", "team")
    )
    lang_codes = []
    for _imp, modname, _isp in pkgutil.walk_packages(package.__path__):
        if is_language_module(modname):
            if modname.startswith("code_"):
                modname = modname.replace("code_", "")
            lang_codes.append(modname)
    return [getlanguage(lang_code) for lang_code in sorted(lang_codes)]
