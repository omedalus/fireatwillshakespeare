"""Main entry point for Fire At Will Shakespeare."""

from models.board import Board
from views.board_renderer import BoardRenderer


def main():
    """Run a simple demo of the board."""
    print("Fire At Will Shakespeare")
    print("=" * 40)
    print()

    # Create a board and initialize with random ships and hostages
    board = Board(rows=8, cols=8)
    board.setup(num_ships=5, num_hostages=3)

    # Render the board
    renderer = BoardRenderer(board)

    print(renderer.render_with_legend())
    print()

    print(f"Ships: {board.ships_remaining()}")
    print(f"Hostages: {board.hostages_remaining()}")


if __name__ == "__main__":
    main()
