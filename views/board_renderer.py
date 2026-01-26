"""ASCII rendering for the game board."""

from models.board import Board
from models.entities import Coordinates, EntityType


class BoardRenderer:
    """Renders a board as ASCII art."""

    # Display symbols for each entity type
    SYMBOLS = {
        EntityType.EMPTY: "·",
        EntityType.SHIP: "S",
        EntityType.HOSTAGE: "H",
    }

    def __init__(self, board: Board):
        """
        Initialize the renderer.

        Args:
            board: The board to render
        """
        self.board = board

    def render(self) -> str:
        """
        Render the board as ASCII art for the player (who sees everything).

        Returns:
            A string representation of the board
        """
        lines = []

        # Header with column letters
        header = "    " + " ".join(chr(ord("A") + i) for i in range(self.board.cols))
        lines.append(header)
        lines.append("   " + "─" * (self.board.cols * 2))

        # Board rows
        for row in range(self.board.rows):
            row_chars = []
            for col in range(self.board.cols):
                entity = self.board.get_entity_at(Coordinates(row, col))
                symbol = self.SYMBOLS.get(entity, "?") if entity else "?"
                row_chars.append(symbol)

            row_str = f"{row + 1} │ " + " ".join(row_chars)
            lines.append(row_str)

        return "\n".join(lines)

    def render_with_legend(self) -> str:
        """
        Render the board with a legend explaining symbols.

        Returns:
            Board with legend
        """
        board_str = self.render()

        legend = [
            "",
            "Legend:",
            f"  {self.SYMBOLS[EntityType.SHIP]} = Ship",
            f"  {self.SYMBOLS[EntityType.HOSTAGE]} = Hostage",
            f"  {self.SYMBOLS[EntityType.EMPTY]} = Empty",
        ]

        return board_str + "\n" + "\n".join(legend)
