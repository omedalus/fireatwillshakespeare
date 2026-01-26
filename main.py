"""Main entry point for Fire At Will Shakespeare."""

from models.board import Board
from models.entities import Coordinates, EndgameResult, EntityType
from views.board_renderer import BoardRenderer


def main():
    """Run a simple demo of the board."""
    print("Fire At Will Shakespeare")
    print("=" * 40)
    print()

    # Prompt for lore context
    print(
        """
Establish Your Lore Context
---------------------------

Before the game begins, you should tell your artillery team (your ally)
about which "lore context" you'll be using to obfuscate your commands.
The "lore context" is a shared narrative frame that your ally will use
to interpret your commands. It can be a movie franchise, an author,
a band, a historical event, or anything else you like. You will use this
lore context to embed your commands in ambiguous language that your ally
will understand, but your enemy will hopefully misinterpret.

Your commands should specify a coordinate position that your ally will
fire upon, but you should do so in a way that can only be understood with
the help of the lore context -- and, moreover, in a way that doesn't reveal
the lore context itself!

Example: The lore context is: "William Shakespeare's plays"
Suppose you want to target coordinate "C4".
DON'T SAY: "Fire at C4." (The enemy will understand this directly, and will simply
    move their ships away from that position.)
DON'T SAY: "The first letter of 'Capulet' and the number of letters in 'Iago'."
    (This is no better than just outright stating the coordinates, because
    even an enemy who doesn't know the lore context can clearly see that the
    first letter of 'Capulet' is 'C' and the number of letters in 'Iago' is 4.)
DON'T SAY: "Juliet's last name, and the number of letters in the name of
    Othello's duplicitous friend." (This is a dead giveaway that your lore context
    is Shakespeare, since both Juliet and Othello are very distinct Shakespearean 
    characters. Upon hearing this, the enemy will quickly guess your lore context
    and decipher your coordinates.)
SAY: "The first letter of the Italian girl's family name, and the number of
    letters in the name of the Black man's duplicitous friend." (This is extremely
    vague to anyone who doesn't know that we're talking about Shakespeare, but
    it's extremely specific if you realize that Shakespeare is the context.)

So, with all that in mind...
What lore context will you and your ally use to encode your commands?
"""
    )
    lore_context = input(
        "Enter your lore context (e.g., 'The plays of William Shakespeare'): "
    ).strip()
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

        endgame = board.check_endgame()
        if endgame == EndgameResult.WIN:
            print("All ships neutralized. You win!")
            break
        if endgame == EndgameResult.LOSE:
            print("All hostages lost. You lose.")
            break

        user_input = input(
            "Enter your obfuscated targeting command (or 'q' to quit): "
        ).strip()
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
