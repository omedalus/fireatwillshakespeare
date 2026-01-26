"""Board representation and operations."""

import random
from typing import List, Optional, Union
from .entities import Coordinates, EndgameResult, EntityType


class Board:
    """
    Represents the game board.

    The board is a grid where entities (ships, hostages) can be placed.
    The player sees everything; the ally sees nothing; the enemy hears everything.
    """

    def __init__(self, rows: int = 8, cols: int = 8):
        """
        Initialize an empty board.

        Args:
            rows: Number of rows (default 8)
            cols: Number of columns (default 8)
        """
        self.rows = rows
        self.cols = cols
        self.grid: List[List[EntityType]] = [
            [EntityType.EMPTY for _ in range(cols)] for _ in range(rows)
        ]

    def setup(self, num_ships: int, num_hostages: int) -> None:
        """
        Randomly place ships and hostages on the board.

        Args:
            num_ships: Number of ships to place
            num_hostages: Number of hostages to place
        """
        # Place ships randomly
        ships_placed = 0
        while ships_placed < num_ships:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.place_entity(Coordinates(row, col), EntityType.SHIP):
                ships_placed += 1

        # Place hostages randomly
        hostages_placed = 0
        while hostages_placed < num_hostages:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.place_entity(Coordinates(row, col), EntityType.HOSTAGE):
                hostages_placed += 1

    def place_entity(self, coordinates: Coordinates, entity_type: EntityType) -> bool:
        """
        Place an entity at the given position.

        Args:
            coordinates: Target board position
            entity_type: EntityType.SHIP or EntityType.HOSTAGE

        Returns:
            True if placement succeeded, False if position invalid or occupied
        """
        if entity_type not in (EntityType.SHIP, EntityType.HOSTAGE):
            return False

        if not self._is_valid_position(coordinates):
            return False

        if self.grid[coordinates.row][coordinates.col] != EntityType.EMPTY:
            return False

        self.grid[coordinates.row][coordinates.col] = entity_type
        return True

    def fire(self, coordinates: Coordinates) -> Optional[EntityType]:
        """
        Fire at a position.

        Args:
            coordinates: Coordinates instance of target position

        Returns:
            The entity type that was hit, or None if position invalid
        """
        if not self._is_valid_position(coordinates):
            return None

        hit_type = self.grid[coordinates.row][coordinates.col]

        if hit_type in (EntityType.SHIP, EntityType.HOSTAGE):
            self.grid[coordinates.row][coordinates.col] = EntityType.EMPTY

        return hit_type

    def move_entity(self, source: Coordinates, destination: Coordinates) -> bool:
        """
        Move an entity from one position to another.
        Used by the enemy to reposition assets.

        Args:
            source: Source position
            destination: Destination position

        Returns:
            True if move succeeded, False otherwise
        """
        if not self._is_valid_position(source):
            return False
        if not self._is_valid_position(destination):
            return False

        entity_type = self.grid[source.row][source.col]

        if entity_type == EntityType.EMPTY:
            return False

        if self.grid[destination.row][destination.col] != EntityType.EMPTY:
            return False

        # Update grid
        self.grid[source.row][source.col] = EntityType.EMPTY
        self.grid[destination.row][destination.col] = entity_type

        return True

    def get_entity_at(self, coordinates: Coordinates) -> Optional[EntityType]:
        """Get the entity type at a position."""
        if not self._is_valid_position(coordinates):
            return None
        return self.grid[coordinates.row][coordinates.col]

    def _is_valid_position(self, coordinates: Coordinates) -> bool:
        """Check if a position is within board bounds."""
        return 0 <= coordinates.row < self.rows and 0 <= coordinates.col < self.cols

    def ships_remaining(self) -> int:
        """Return the number of ships still on the board."""
        return sum(1 for row in self.grid for cell in row if cell == EntityType.SHIP)

    def hostages_remaining(self) -> int:
        """Return the number of hostages still on the board."""
        return sum(1 for row in self.grid for cell in row if cell == EntityType.HOSTAGE)

    def check_endgame(self) -> Optional[EndgameResult]:
        """Return WIN, LOSE, or None depending on remaining ships and hostages."""
        if self.ships_remaining() == 0:
            return EndgameResult.WIN
        if self.hostages_remaining() == 0:
            return EndgameResult.LOSE
        return None
