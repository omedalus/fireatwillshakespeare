"""Main entry point for Fire At Will Shakespeare."""

import random
from models.board import Board
from views.board_renderer import BoardRenderer


def main():
    """Run a simple demo of the board."""
    print("Fire At Will Shakespeare")
    print("=" * 40)
    print()

    # Create a board
    board = Board(rows=8, cols=8)

    # Place 5 ships randomly
    ships_placed = 0
    while ships_placed < 5:
        row = random.randint(0, 7)
        col = random.randint(0, 7)
        if board.place_ship(row, col):
            ships_placed += 1

    # Place 3 hostages randomly
    hostages_placed = 0
    while hostages_placed < 3:
        row = random.randint(0, 7)
        col = random.randint(0, 7)
        if board.place_hostage(row, col):
            hostages_placed += 1

    # Render the board
    renderer = BoardRenderer(board)

    print(renderer.render_with_legend())
    print()

    print(f"Ships: {board.ships_remaining()}")
    print(f"Hostages: {board.hostages_remaining()}")


if __name__ == "__main__":
    main()
