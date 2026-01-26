"""Main entry point for Fire At Will Shakespeare."""

from models.board import Board
from models.entities import Coordinates, EntityType
from views.board_renderer import BoardRenderer


def main():
    """Run a simple demo of the board."""
    print("Fire At Will Shakespeare")
    print("=" * 40)
    print()

    # Create a board and initialize with random ships and hostages
    board = Board(rows=8, cols=8)
    board.setup(num_ships=5, num_hostages=3)

    renderer = BoardRenderer(board)

    while True:
        print(renderer.render_with_legend())
        print()
        print(f"Ships: {board.ships_remaining()}")
        print(f"Hostages: {board.hostages_remaining()}")

        # Check end conditions before prompting the next shot
        if board.ships_remaining() == 0:
            print("All ships neutralized. You win!")
            break
        if board.hostages_remaining() == 0:
            print("All hostages lost. You lose.")
            break

        user_input = input("Enter target (e.g., B3) or 'q' to quit: ").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("Exiting game.")
            break

        try:
            coordinates = Coordinates.from_string(user_input)
        except ValueError as exc:
            print(f"Invalid input: {exc}")
            print()
            continue

        hit = board.fire(coordinates)
        if hit is None:
            print("That coordinate is outside the board.")
        elif hit == EntityType.EMPTY:
            print("Miss: empty water.")
        elif hit == EntityType.SHIP:
            print("Hit: ship destroyed!")
        elif hit == EntityType.HOSTAGE:
            print("Oh no: you hit a hostage.")

        print()


if __name__ == "__main__":
    main()
