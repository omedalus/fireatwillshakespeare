"""Main entry point for Fire At Will Shakespeare."""

import os
import sys
from agents.ally import Ally
from agents.enemy import Enemy
from models.board import Board
from models.entities import EndgameResult, EntityType
from views.board_renderer import BoardRenderer
import openai
import dotenv


def main():
    """Run the game via a text interface on the command line."""

    dotenv.load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    openai_client = openai.Client(api_key=OPENAI_API_KEY)

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
DON'T SAY: "Fire at C4." (The enemy will understand this directly and can take
    protective measures, such as deploying limited-use Chaff that shields a square
    for one turn.)
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

Important: Due to military policy, your artillery team rotates out after each shot.
A fresh crew of green soldiers arrives for every turn with no memory of previous
instructions or patterns. This means you cannot rely on them learning or remembering
your code over time—you must make each instruction clear *in isolation*.    

So, with all that in mind...
What lore context will you and your ally use to encode your commands?
"""
    )
    lore_context = input(
        "Enter your lore context (e.g., 'The plays of William Shakespeare'): "
    ).strip()
    print()

    ally = Ally()
    ally.setup(
        lore_context=lore_context,
        openai_client=openai_client,
    )

    enemy = Enemy()
    enemy.setup(openai_client=openai_client)

    # Create a board and initialize with random ships and hostages
    board = Board(rows=8, cols=8)
    board.setup(num_ships=5, num_hostages=3)

    renderer = BoardRenderer(board)

    # The first turn is always NOT an injection attack turn
    # We set this to True so that the first action in the loop
    # flips it to False
    is_injection_turn = True

    while True:
        # Every other turn is an injection attack turn
        is_injection_turn = not is_injection_turn

        board.start_turn()
        ally.start_turn(board)
        enemy.start_turn(board)

        print(renderer.render_with_legend())
        print(renderer.describe())
        print()
        print(f"Ships: {board.ships_remaining()}")
        print(f"Hostages: {board.hostages_remaining()}")

        targeting_instructions = ""
        if not is_injection_turn:
            targeting_instructions = input(
                "Enter your obfuscated targeting command (or 'q' to quit): "
            ).strip()
            if targeting_instructions.lower() in {"q", "quit", "exit"}:
                print("Exiting game.")
                break

        else:
            print("It's the enemy's turn to attempt an injection attack...")
            targeting_instructions = enemy.inject_spoofed_message()

            print("The enemy has sent the following spoofed message:")
            print(targeting_instructions)
            print()

        fire_coordinates = None
        chaff_coords = None
        try:
            print("Ally is receiving your targeting instructions...")
            fire_coordinates = ally.receive_targeting_instructions(
                targeting_instructions=targeting_instructions
            )

            if not is_injection_turn:
                print("Enemy is overhearing your targeting instructions...")
                try:
                    chaff_coords = enemy.overhear_targeting_instructions(
                        targeting_instructions
                    )
                except ValueError as exc:
                    print(f"Error during Enemy phase: {exc}")
                    print()

                if chaff_coords:
                    board.deploy_chaff(chaff_coords)
                    print(
                        f"Enemy has deployed chaff at {chaff_coords} to block your shot."
                    )
                    print()

        except ValueError as exc:
            print(f"Error during Ally phase: {exc}")
            print()

        if not fire_coordinates:
            print(
                "Ally passes this turn. They either could not decode the message, "
                "or determined that it was an injection attack."
            )
            print()
        else:
            hit = board.fire(fire_coordinates)
            if hit is None:
                print("That coordinate is outside the board.")
            elif hit == EntityType.EMPTY:
                print("Miss: empty water.")
            elif hit == EntityType.CHAFF:
                print("Shot blocked by chaff!")
            elif hit == EntityType.SHIP:
                print("Hit: ship destroyed!")
            elif hit == EntityType.HOSTAGE:
                print("Oh no: you hit a hostage.")

        endgame = board.check_endgame()
        if endgame == EndgameResult.WIN:
            print("All ships neutralized. You win!")
            break
        if endgame == EndgameResult.LOSE:
            print("All hostages lost. You lose.")
            break

        # The enemy can now re-evaluate their lore context here based on the ally's action
        enemy.observe_opponent_action(fire_coordinates)

        print()


if __name__ == "__main__":
    main()
