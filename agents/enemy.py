"""Enemy logic for eavesdropping on player commands."""

from typing import Optional

import openai

from models.board import Board
from models.entities import Coordinates

from utils.gpt import GptConversation, JSONSchemaFormat
from views.board_renderer import BoardRenderer

# TODO: THIS IS STILL MOSTLY JUST A COPY OF THE ALLY CLASS. NEED TO CUSTOMIZE IT FOR THE ENEMY.


class Enemy:
    """The enemy that eavesdrops on player messages."""

    def __init__(self, openai_client: openai.Client) -> None:
        self._openai_client = openai_client
        self._convo: Optional[GptConversation] = None
        self._board: Optional[Board] = None

        self._event_history = []

    def start_turn(self, board: Board) -> None:
        """Prepare for a new turn."""
        self._event_history.append({})
        self._board = board
        self._convo = GptConversation(openai_client=self._openai_client)
        renderer = BoardRenderer(board)

        self._convo.add_system_message(
            """
We're playing an asymmetrical social game that's a hybrid of Battleship and Codenames!

We're playing a "bad guy" role in this game. We're overhearing messages on a compromised
channel (we're the ones who compromised it, teehee!) being transmitted by our opponent.
He's trying to communicate target coordinates on a Battleship board to an ally of his.

The board is a grid that contains our ships (which we want to protect) and hostages
that are valuable to the opponent (which we want to trick him into hitting).

Both the player and the ally know that the channel is compromised, so they are trying to
communicate in a highly obfuscated manner using a shared "lore context" that only they
know about.

This "lore context" is a shared narrative frame (like a movie franchise, an author, a band,
a historical event, a field of science, etc.) that allows the ally to interpret the
opponent's ambiguous messages. They're deliberately trying to make it very hard to understand
the targeting coordinates without knowing the lore context.

Our job is to see if we can understand it anyway! :D

In every turn, we can deploy Chaff to one square to block incoming artillery for that turn.
This is a countermeasure we can use when we think we've inferred the target.
(Chaff deployment is disabled when you're down to your last ship, so be careful!)
If we can correctly infer the target coordinates, we can deploy Chaff there to protect
our ship from being hit.
We also have at our disposal the ability, on certain occasions, to inject a spoofed message
into the channel to try to mislead the opponent's ally. The ally is aware of our ability
to do this, and is being vigilant against such potential injection attacks.
"""
        )

        # Add previous events here.
        if len(self._event_history) > 1:
            self._convo.add_system_message(
                "Determining the lore context is an ongoing deductive process that "
                "involves piecing together clues over multiple turns. "
                "Here are some notes from previous turns to help you get up to speed."
            )
            for event in self._event_history:
                if "targeting_instructions" in event:
                    self._convo.add_user_message(event.get("targeting_instructions"))
                if "fired_coordinates" in event:
                    fired_coordinates = event.get("fired_coordinates")
                    if fired_coordinates is None:
                        self._convo.add_system_message(
                            "In response to that message, the artillery team chose to PASS."
                        )
                    else:
                        self._convo.add_system_message(
                            f"In response to that message, the artillery team fired at position: {fired_coordinates}"
                        )
                if "lore_belief" in event:
                    lore_belief = event.get("lore_belief") or "(No notes provided.)"
                    self._convo.add_assistant_message(lore_belief)

        self._convo.add_system_message(
            f"""
The board currently looks like this.

ASCII:
{renderer.render_with_legend()}

Description:
{renderer.describe()}
"""
        )

    def overhear_targeting_instructions(
        self,
        targeting_instructions: str,
    ) -> Optional[Coordinates]:
        """
        Decode an obfuscated message into target coordinates, without explicit
        knowledge of the lore context.
        """
        if self._convo is None:
            raise RuntimeError("Conversation has not been started.")
        if self._board is None:
            raise RuntimeError("Board has not been set.")

        if (
            self._event_history is None
            or len(self._event_history) == 0
            or self._event_history[-1] is None
        ):
            raise RuntimeError("Event history has not been initialized.")

        self._event_history[-1]["targeting_instructions"] = targeting_instructions

        self._convo.add_system_message(
            """
We're about to receive a new message from the opponent. He's trying to convey some kind of
information to his ally over a channel that he knows is compromised. Therefore, he's deliberately
using obfuscated verbiage that (in theory) only makes sense if you know the shared lore context.

He might be trying to communicate target coordinates of one of our
ships, or he might be trying to tell the ally to avoid hitting a hostage. (There's even a chance
that he's trying to trick us by sending a message that doesn't convey any information at all
-- but this is unlikely, because doing so is likely to also confuse his ally.)

Either way, here's what he's saying:
"""
        )
        self._convo.add_user_message(targeting_instructions)

        print("Enemy is trying to determine lore context...")
        self._convo.submit_system_message(
            """
Let's think step by step.
Do we already know the lore context that the opponent and his ally are using to encode their
messages?
If we do, great! We can use that to try to decode the message. (We can do that later.)
If not, can we infer it from the message itself? Does the message leak clues about the 
lore context?

Don't worry about decoding the message itself just yet -- unless the decoding process helps us
infer the lore context. For example, given that we know that the opponent is trying to convey
target coordinates on a Battleship board, determining that the message references our ships or
hostages might help us infer the lore context. For now, though, let's focus on whether we can
determine the lore context.

Here are some tricks you can use to glean lore context clues from the message:
1. Look for distinctive phrases, names, or terms in the message that might be tied to a specific
    lore context.
2. If the message talks about characters, events, or concepts, see if they align with 
    any well-known franchises, authors, bands, or historical events.
3. If the message mentions "the first letter of X" or "the number of letters in Y", then that
    narrows down the possibilities for X and Y. For example, if X is a character's name, then 
    that means that the name has to start with letters A-H. If it's "number of letters", then
    that means that the name has to have between 1 and 8 letters. Etc.

Even if we can't determine the exact lore context, can we at least narrow it down? What *kind*
of lore context is it likely to be? Maybe we don't know specifics, but what *can* we infer
about it?
"""
        )

        if not self._board.can_deploy_chaff():
            print("Chaff deployment is disabled (only one ship remains).")
            return None

        print("Enemy is trying to determine the target coordinates...")
        self._convo.submit_system_message(
            """
Next, let's try to decode the message itself.
If we have determined the lore context, awesome! We have just as much ability to decode the
message as the ally does.

If we *don't* know the lore context, we can still try to decode the message using any clues
we've gleaned, as well as the board state and the message itself. The player might have let
some information leak about the square they're targeting.

We not only need to glean the target coordinates, but also whether the opponent is trying to
tell his ally to hit a ship, or whether he's trying to tell them to avoid hitting a hostage.

It's also possible that the opponent is trying to tell his ally multiple coordinates at once.
This is a less likely scenario, but it's worth considering.

Here are some examples of ways that the message might reference the board state:
- If the message mentions the "number of letters in X", then that number is probably not 1 or 2.
    After all, there are very few 1- or 2-letter names. Therefore, the number is probably 
    between 3 and 8, which narrows down the possible coordinates. If we only have one ship
    at high coordinates, then it's probably talking about that one.
- If the message references directional or positional clues like "upper left", then we can use
    that to narrow down the possible coordinates.

All of that is moot if we know the lore context, of course. In that case, we can just use
that to decode the message directly.

So, let's try to do it! Let's figure out:
- What target coordinates is the opponent trying to convey?
- Is he trying to tell his ally to hit a ship, or avoid hitting a hostage?

Keep in mind that the opponent is engaged in information warfare here. He knows that we're
listening in, so he's deliberately trying to make it hard for us to understand the message.
He might be messing with us. He might be transmitting false information. He might be
trying to trick us into misinterpreting the message.

First, discuss your reasoning. If you need to do any "scratchpad"
calculations, do so. If you need to "think aloud" to arrive at the coordinates, do so.
I'd like to hear your thoughts as you go.
"""
        )

        print("Enemy is deciding where to deploy chaff...")
        self._convo.submit_system_message(
            """
At this point, we should decide where to deploy our Chaff countermeasure.
The player has sent the message, and we've done our best to decode it.
The player's artillery team hasn't fired yet, fortunately. That means that we can
still deploy Chaff to one square on the board to block incoming artillery for this turn.

We should decide which square to Chaff based on our best guess of where the player
is trying to target.

Remember, we only get to deploy Chaff to one square per turn. We should pick the square
that we think is most likely to be targeted by the player's artillery, *if* that square
contains one of our ships. If we're not confident about where the player is targeting,
we should pick a square that contains one of our ships for good measure.

If the player is targeting a hostage for some reason, we don't need to Chaff that square,
since we want the artillery to hit the hostages. We're the bad guys, remember! :)

If the player is targeting an empty square, and we're very confident about that, then we
might want to Chaff it just to mess with them (they'll think we're protecting a ship there!).

Basically, just remember that our goal is to protect our ships from being hit by artillery,
while letting the hostages be hit -- all in the context of this information warfare scenario.

With all of that in mind, discuss which square we should deploy Chaff to, and why.
"""
        )

        self._convo.submit(
            json_response=JSONSchemaFormat(
                name="chaff_deployment",
                description="JSON formalization of where to deploy chaff this turn.",
                schema={
                    "col": (
                        str,
                        "The letter of the column (A-H) of the desired chaff square.",
                        ["A", "B", "C", "D", "E", "F", "G", "H"],
                    ),
                    "row": (
                        int,
                        "The number of the row (1-8) of the desired chaff square.",
                        (1, 8),
                    ),
                    "lore_deduction": (
                        str,
                        (
                            "A brief summary of what we've inferred about the lore context "
                            "so far. If we've nailed the lore context, state it explicitly. "
                            "If we aren't sure yet, then write some notes about the clues "
                            "we've got so far, so that we can resume investigating later."
                        ),
                    ),
                    "targeting_explanation": (
                        str,
                        (
                            "A brief explanation of the reasoning behind our decision of "
                            "where to deploy chaff. Include any relevant inferences about "
                            "the target coordinates that informed our decision."
                        ),
                    ),
                },
            )
        )
        col = self._convo.get_last_reply_dict_field("col")
        row = self._convo.get_last_reply_dict_field("row")
        lore_deduction = self._convo.get_last_reply_dict_field("lore_deduction")
        targeting_explanation = self._convo.get_last_reply_dict_field(
            "targeting_explanation"
        )
        if not col or not row:
            raise ValueError("Could not decode target coordinates from message.")

        coordinates = Coordinates.from_string(f"{col}{row}")
        print(f"Enemy is deploying chaff to: {coordinates}")
        print(f"  Lore Deduction: {lore_deduction}")
        print(f"  Targeting Explanation: {targeting_explanation}")

        self._event_history[-1]["lore_belief"] = lore_deduction

        self._convo.submit_system_message(
            f"""
We have deployed chaff to {coordinates}.
Rationale: {targeting_explanation}

To recap, here's what we know about the lore context so far:
{lore_deduction}
"""
        )

        return coordinates

    def observe_opponent_action(
        self,
        fired_coordinates: Optional[Coordinates],
    ) -> None:
        if self._convo is None:
            raise RuntimeError("Conversation has not been started.")
        if self._board is None:
            raise RuntimeError("Board has not been set.")

        if (
            self._event_history is None
            or len(self._event_history) == 0
            or self._event_history[-1] is None
        ):
            raise RuntimeError("Event history has not been initialized.")

        self._convo.add_system_message(
            """
The opponent's artillery team has now had a chance to hear and evaluate the 
last message for themselves. We are now observing the actions they took as a result
of their evaluation, to see if we can glean any additional insights about the
lore context. After all, they have the advantage of knowing the lore context, so
their actions might reveal additional clues.
"""
        )

        self._convo.add_system_message(
            f"""
Just as a reminder, I'll replay the opponent's last message here for your reference.
"""
        )
        self._convo.add_user_message(
            self._event_history[-1].get("targeting_instructions")
        )

        if fired_coordinates is None:
            self._convo.add_system_message(
                """
In response to that message,
the artillery team has chosen not to fire this turn. They chose to PASS.

This could be because of a number of reasons:

- They couldn't decode the message at all.

- They determined that the message was an injection attack from us, i.e. that the message
    was a malicious spoof rather than an authentic targeting instruction.

- They decoded the message, but determined that firing at the indicated coordinates
    would risk hitting a hostage, so they chose to hold fire.
"""
            )
        else:
            self._convo.add_system_message(
                f"""
In response to that message,
the artillery team fired at position: {fired_coordinates}

That means that the artillery team interpreted the opponent's message as indicating that
they should shoot at {fired_coordinates}.
"""
            )

        print("Enemy is re-evaluating lore context based on opponent action...")
        self._convo.submit_system_message(
            f"""
The artillery team's action might give us additional clues about the lore context.
Let's re-examine the message and see if we can glean any new insights based on
the artillery team's action.
"""
        )

        print("Enemy is leaving notes for future turns...")
        self._convo.submit_system_message(
            f"""
What's your leading hypothesis about the lore context at this point?
Have we nailed it down, or are we still uncertain? If we're still uncertain,
what clues do we have so far that we can build on in future turns?
"""
        )
        lore_belief = self._convo.get_last_reply_str()
        print("Enemy's current lore context belief:")
        print(lore_belief)

        self._event_history[-1]["lore_belief"] = lore_belief
