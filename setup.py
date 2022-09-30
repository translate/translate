#!/usr/bin/env python
#
# Copyright 2006-2013 Zuza Software Foundation
#
# This file is part of Translate.
#
# Translate is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Translate is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Translate; if not, see <http://www.gnu.org/licenses/>.

import re

from setuptools import setup


def parse_requirements(file_name):
    """Parses a pip requirements file and returns a list of packages.

    Use the result of this function in the ``install_requires`` field.
    Copied from cburgmer/pdfserver.
    """
    requirements = []
    with open(file_name) as fh:
        for line in fh:
            # Ignore comments, blank lines and included requirements files
            if re.match(r"(\s*#)|(\s*$)|(-r .*$)", line):
                continue

            if re.match(r"\s*-e\s+", line):
                requirements.append(re.sub(r"\s*-e\s+.*#egg=(.*)$", r"\1", line))
            elif not re.match(r"\s*-f\s+", line):
                requirements.append(line.rstrip("\n"))

    return requirements


# Generate extras requires
def parse_extra_requires(filename):
    extras_require = {"all": []}
    with open(filename) as requirements:
        for line in requirements:
            line = line.strip()
            # Skip comments, inclusion or blank lines
            if not line or line.startswith("-r") or line.startswith("#"):
                continue
            dependency, section = line.split("#")
            dependency = dependency.strip()
            section = section.strip()
            if section not in extras_require:
                extras_require[section] = [dependency]
            else:
                extras_require[section].append(dependency)
            extras_require["all"].append(dependency)
    return extras_require


setup(
    extras_require=parse_extra_requires("requirements/optional.txt"),
    install_requires=parse_requirements("requirements/required.txt"),
)
