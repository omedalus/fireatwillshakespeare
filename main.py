"""Main entry point for Fire At Will Shakespeare."""

from models.board import Board
from views.board_renderer import BoardRenderer


def main():
    """Run a simple demo of the board."""
    print("Fire At Will Shakespeare")
    print("=" * 40)
    print()

    # Create a board
    board = Board(rows=8, cols=8)

    # Place some ships and hostages for demonstration
    board.place_ship(2, 3)
    board.place_ship(5, 1)
    board.place_ship(4, 6)

    board.place_hostage(1, 1)
    board.place_hostage(6, 5)

    # Render the board
    renderer = BoardRenderer(board)

    print(renderer.render_with_legend())
    print()

    print(f"Ships: {board.ships_remaining()}")
    print(f"Hostages: {board.hostages_remaining()}")


if __name__ == "__main__":
    main()
