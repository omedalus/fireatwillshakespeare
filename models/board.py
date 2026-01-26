"""Board representation and operations."""

from typing import List, Optional, Tuple
from .entities import Entity, EntityType, Position


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
        self.ships: List[Position] = []
        self.hostages: List[Position] = []
        self.hits: List[Position] = []

    def place_ship(self, row: int, col: int) -> bool:
        """
        Place a ship at the given position.

        Args:
            row: Row index
            col: Column index

        Returns:
            True if placement succeeded, False if position invalid or occupied
        """
        if not self._is_valid_position(row, col):
            return False

        if self.grid[row][col] != EntityType.EMPTY:
            return False

        self.grid[row][col] = EntityType.SHIP
        self.ships.append(Position(row, col))
        return True

    def place_hostage(self, row: int, col: int) -> bool:
        """
        Place a hostage at the given position.

        Args:
            row: Row index
            col: Column index

        Returns:
            True if placement succeeded, False if position invalid or occupied
        """
        if not self._is_valid_position(row, col):
            return False

        if self.grid[row][col] != EntityType.EMPTY:
            return False

        self.grid[row][col] = EntityType.HOSTAGE
        self.hostages.append(Position(row, col))
        return True

    def fire(self, row: int, col: int) -> Optional[EntityType]:
        """
        Fire at a position.

        Args:
            row: Row index
            col: Column index

        Returns:
            The entity type that was hit, or None if position invalid
        """
        if not self._is_valid_position(row, col):
            return None

        hit_type = self.grid[row][col]

        if hit_type == EntityType.SHIP:
            self.ships.remove(Position(row, col))
        elif hit_type == EntityType.HOSTAGE:
            self.hostages.remove(Position(row, col))

        self.grid[row][col] = EntityType.HIT
        self.hits.append(Position(row, col))

        return hit_type

    def move_entity(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        """
        Move an entity from one position to another.
        Used by the enemy to reposition assets.

        Args:
            from_row: Source row
            from_col: Source column
            to_row: Destination row
            to_col: Destination column

        Returns:
            True if move succeeded, False otherwise
        """
        if not self._is_valid_position(from_row, from_col):
            return False
        if not self._is_valid_position(to_row, to_col):
            return False

        entity_type = self.grid[from_row][from_col]

        if entity_type == EntityType.EMPTY or entity_type == EntityType.HIT:
            return False

        if self.grid[to_row][to_col] != EntityType.EMPTY:
            return False

        # Update grid
        self.grid[from_row][from_col] = EntityType.EMPTY
        self.grid[to_row][to_col] = entity_type

        # Update tracking lists
        old_pos = Position(from_row, from_col)
        new_pos = Position(to_row, to_col)

        if entity_type == EntityType.SHIP:
            self.ships.remove(old_pos)
            self.ships.append(new_pos)
        elif entity_type == EntityType.HOSTAGE:
            self.hostages.remove(old_pos)
            self.hostages.append(new_pos)

        return True

    def get_entity_at(self, row: int, col: int) -> Optional[EntityType]:
        """Get the entity type at a position."""
        if not self._is_valid_position(row, col):
            return None
        return self.grid[row][col]

    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within board bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def ships_remaining(self) -> int:
        """Return the number of ships still on the board."""
        return len(self.ships)

    def hostages_remaining(self) -> int:
        """Return the number of hostages still on the board."""
        return len(self.hostages)
