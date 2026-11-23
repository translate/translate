"""
This module represents the Catalan language.

Catalan does **not** use the inverted opening question and exclamation marks
(``¿``, ``¡``) that Spanish uses, so :mod:`translate.lang.es` must not be
reused for it.

.. seealso:: :wp:`Catalan_language`
"""

from translate.lang import common


class ca(common.Common):
    """This class represents Catalan."""

    ignoretests = {
        "all": ["acronyms", "simplecaps", "startcaps"],
    }
