#
# Copyright 2016 Zuza Software Foundation
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

"""This module represents the Brazilian Portuguese language.

.. seealso:: :wp:`Brazilian_Portuguese`
"""


from translate.lang.common import Common


class pt_BR(Common):
    """This class represents Brazilian Portugues."""

    miscpunc = Common.miscpunc.replace("·", "")  # Middle dot is not valid.

    validaccel = "ABCDEFGHIJKLMNOPQRSTUVXYZ" "abcdefghijklmnopqrstuvxyz" "1234567890"
