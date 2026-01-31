"""Game entities: Ships, Hostages, etc."""

from enum import Enum
from dataclasses import dataclass


class EntityType(Enum):
    """Types of entities that can exist on the board."""

    EMPTY = "empty"
    SHIP = "ship"
    HOSTAGE = "hostage"
    CHAFF = "chaff"


class EndgameResult(Enum):
    """Possible game outcomes."""

    WIN = "win"
    LOSE = "lose"


@dataclass(frozen=True)
class Coordinates:
    """A position on the board."""

    row: int
    col: int

    @classmethod
    def from_string(cls, value: str) -> "Coordinates":
        """Create Coordinates from a string like "B6" (column letter + 1-based row)."""
        normalized = value.strip().upper()
        if len(normalized) < 2:
            raise ValueError(
                "Coordinate string must be at least 2 characters, like 'A1'."
            )

        column_letter = normalized[0]
        if column_letter < "A" or column_letter > "Z":
            raise ValueError("Column must be a letter A-Z.")

        try:
            row_number = int(normalized[1:])
        except ValueError as exc:
            raise ValueError("Row must be a number after the column letter.") from exc

        if row_number < 1:
            raise ValueError("Row number must be 1 or greater.")

        row = row_number - 1
        col = ord(column_letter) - ord("A")
        return cls(row=row, col=col)

    def __iter__(self):
        return iter((self.row, self.col))

    def __repr__(self):
        # Human-friendly format like "B5" (column letter, then 1-based row)
        column_letter = chr(ord("A") + self.col)
        return f"{column_letter}{self.row + 1}"


@dataclass
class Entity:
    """An entity on the board."""

    entity_type: EntityType
    position: Coordinates

    def __repr__(self):
        return f"{self.entity_type.value} at {self.position}"


@dataclass
class ObservedArtilleryAction:
    """A recorded artillery action with its targeting instructions and fired coordinates."""

    targeting_instructions: str
    fired_coordinates: Coordinates
