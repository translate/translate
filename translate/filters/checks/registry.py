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

"""Mapping of the project names accepted by pofilter to their checkers."""

from translate.filters.checks.cclicense import CCLicenseChecker
from translate.filters.checks.drupal import DrupalChecker
from translate.filters.checks.gnome import GnomeChecker
from translate.filters.checks.ios import IOSChecker
from translate.filters.checks.kde import KdeChecker
from translate.filters.checks.libreoffice import LibreOfficeChecker
from translate.filters.checks.minimal import MinimalChecker, ReducedChecker
from translate.filters.checks.mozilla import MozillaChecker
from translate.filters.checks.openoffice import OpenOfficeChecker
from translate.filters.checks.standard import StandardChecker
from translate.filters.checks.term import TermChecker

projectcheckers = {
    "minimal": MinimalChecker,
    "standard": StandardChecker,
    "reduced": ReducedChecker,
    "openoffice": OpenOfficeChecker,
    "libreoffice": LibreOfficeChecker,
    "mozilla": MozillaChecker,
    "kde": KdeChecker,
    "wx": KdeChecker,
    "gnome": GnomeChecker,
    "creativecommons": CCLicenseChecker,
    "drupal": DrupalChecker,
    "terminology": TermChecker,
    "ios": IOSChecker,
}
