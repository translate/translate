"""
This module represents the Toki Pona language.

.. seealso:: :wp:`Toki_Pona`
"""

from translate.lang import common


class tok(common.Common):
    """This class represents Toki Pona."""

    ignoretests = {"all": ["simplecaps", "startcaps"]}
