#
# Copyright 2004-2011 Zuza Software Foundation
# 2013, 2016 F Wolff
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

"""
This is a set of validation checks that can be performed on translation
units.

Derivatives of UnitChecker (like StandardUnitChecker) check translation units,
and derivatives of TranslationChecker (like StandardChecker) check
(source, target) translation pairs.

When adding a new test here, please document and explain their behaviour on the
:doc:`pofilter tests </commands/pofilter_tests>` page.
"""

from translate.filters.checks.cclicense import CCLicenseChecker
from translate.filters.checks.checker import TranslationChecker, UnitChecker
from translate.filters.checks.config import CheckerConfig
from translate.filters.checks.drupal import DrupalChecker
from translate.filters.checks.exceptions import FilterFailure, SeriousFilterFailure
from translate.filters.checks.gnome import GnomeChecker
from translate.filters.checks.ios import IOSChecker
from translate.filters.checks.kde import KdeChecker
from translate.filters.checks.libreoffice import LibreOfficeChecker
from translate.filters.checks.minimal import MinimalChecker, ReducedChecker
from translate.filters.checks.mozilla import L20nChecker, MozillaChecker
from translate.filters.checks.openoffice import OpenOfficeChecker, openofficeconfig
from translate.filters.checks.registry import projectcheckers
from translate.filters.checks.standard import StandardChecker
from translate.filters.checks.tee import TeeChecker
from translate.filters.checks.term import TermChecker
from translate.filters.checks.unit import StandardUnitChecker

__all__ = [
    "CCLicenseChecker",
    "CheckerConfig",
    "DrupalChecker",
    "FilterFailure",
    "GnomeChecker",
    "IOSChecker",
    "KdeChecker",
    "L20nChecker",
    "LibreOfficeChecker",
    "MinimalChecker",
    "MozillaChecker",
    "OpenOfficeChecker",
    "ReducedChecker",
    "SeriousFilterFailure",
    "StandardChecker",
    "StandardUnitChecker",
    "TeeChecker",
    "TermChecker",
    "TranslationChecker",
    "UnitChecker",
    "openofficeconfig",
    "projectcheckers",
]
