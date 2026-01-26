"""Game entities: Ships, Hostages, etc."""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class EntityType(Enum):
    """Types of entities that can exist on the board."""

    EMPTY = "empty"
    SHIP = "ship"
    HOSTAGE = "hostage"
    HIT = "hit"  # After firing


@dataclass
class Position:
    """A position on the board."""

    row: int
    col: int

    def __iter__(self):
        return iter((self.row, self.col))

    def __repr__(self):
        return f"({self.row}, {self.col})"


@dataclass
class Entity:
    """An entity on the board."""

    entity_type: EntityType
    position: Position

    def __repr__(self):
        return f"{self.entity_type.value} at {self.position}"
