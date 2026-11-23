#
# Copyright 2026 Zuza Software Foundation
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

"""Bound work caused by YAML aliases during translation extraction."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from translate.storage.base import ParseError

if TYPE_CHECKING:
    from collections.abc import Generator


DEFAULT_MAX_YAML_NODES = 50_000
DEFAULT_MAX_YAML_UNITS = 20_000


class YAMLTraversalBudget:
    """Count visits, including repeated walks through the same aliased node."""

    def __init__(
        self,
        max_nodes: int | None = DEFAULT_MAX_YAML_NODES,
        max_units: int | None = DEFAULT_MAX_YAML_UNITS,
    ) -> None:
        self.max_nodes = max_nodes
        self.max_units = max_units
        self.reset()

    def reset(self) -> None:
        """Start a new document traversal."""
        self.nodes = 0
        self.units = 0
        self.active: set[int] = set()

    @contextmanager
    def visit(self, node: object) -> Generator[None]:
        """Count one node visit and reject cycles in the active traversal path."""
        self.nodes += 1
        if self.max_nodes is not None and self.nodes > self.max_nodes:
            raise ParseError(f"YAML exceeds the {self.max_nodes} node extraction limit")

        if not isinstance(node, (dict, list)):
            yield
            return

        identity = id(node)
        if identity in self.active:
            raise ParseError("YAML contains a cyclic collection")
        self.active.add(identity)
        try:
            yield
        finally:
            self.active.remove(identity)

    def count_unit(self) -> None:
        """Count an extracted unit before creating it."""
        self.units += 1
        if self.max_units is not None and self.units > self.max_units:
            raise ParseError(f"YAML exceeds the {self.max_units} unit extraction limit")
