"""Logic for checking if commands are likely to be spoofs."""

from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import openai

from models.entities import Coordinates, EntityType
from models.board import Board

from utils.gpt import GptConversation, JSONSchemaFormat


class SpoofChecker:
    """
    A helper class that quickly performs a few heuristic checks in a naive context
    to determine whether a given targeting instruction is likely to be a spoof
    or not.
    """

    def __init__(self) -> None:
        self._board: Optional[Board] = None
        self.openai_client: Optional[openai.Client] = None
        # The ally is stateless by design; no message history is retained

    def setup(self, openai_client: openai.Client) -> None:
        self.openai_client = openai_client

    def start_turn(self, board: Board) -> None:
        """Prepare for a new turn."""
        self._board = board

    def _start_convo(self, targeting_message: str) -> GptConversation:
        if self.openai_client is None:
            raise RuntimeError("SpoofChecker not initialized with OpenAI client.")
        if self._board is None:
            raise RuntimeError("SpoofChecker has not started a turn yet.")

        convo = GptConversation(openai_client=self.openai_client)
        convo.add_system_message(
            f"""
We're playing a game similar to a cross between Battleship and Codenames.
We're supposed to target a specific coordinate on a Battleship board in
standard Battleship coordinate notation (like 'B6' for column B, row 6).
The board is {self._board.rows} rows by {self._board.cols} columns.
Rows are designated by numbers from top to bottom, while columns are designated
by letters from left to right.
A1 is the upper left corner.

However, we don't know the target coordinate directly. Instead, we're supposed
to interpret them based on clues embedded in a message that references some
narrative "lore context" that only we and our teammate know about.
The "lore context" is a shared narrative frame -- i.e. a movie franchise, an author,
a band, a historical event, a class of scientific trivia, etc. -- that allows us 
to interpret ambiguous messages correctly. The "lore context" essentially works 
as a "cognitive codebook" that allows us to decode our teammate's messages while
they're being intentionally vague.

In this game turn, I'm going to show you a message that encodes target coordinates
using our shared lore context. Your job is to analyze the message and answer some
questions about it.

I won't reveal the lore context to you yet. We'll do that later.
"""
        )
        convo.add_user_message(
            f"""
Here is the message we need to decipher:
---
{targeting_message}

"""
        )

        return convo

    def _judge_lore_leakage(
        self,
        targeting_instructions: str,
    ) -> str:
        """Judge how much information leaks about the lore context."""
        convo = self._start_convo(targeting_instructions)

        convo.submit_developer_message(
            """
Now that you know the message, your job is to try to determine the lore context.
Is it a TV show? If so, which TV show?
Is it a book or book series? If so, which one?
Is it a movie franchise? If so, which one?
Based on the message alone, can you determine the lore context?
If you can't determine it entirely, can you at least narrow it down to a few possibilities?

Give a thorough and detailed discussion about what the possible lore contexts are.
Show your reasoning as you go. I'd like to hear your thought process.
"""
        )
        convo.submit(
            json_response=JSONSchemaFormat(
                name="lore_context_leakage_analysis",
                description="JSON formalization of the lore context leakage analysis.",
                schema={
                    "lore_context_possibilities": (
                        str,
                        (
                            "A succinct listing of what the possible lore contexts are, "
                            "based on the message alone. If you can determine it exactly, "
                            "state that. If you can't determine it at all, say 'unknown'."
                        ),
                    ),
                    "explanation": (
                        str,
                        (
                            "A brief but detailed explanation of your reasoning process for "
                            "arriving at these possibilities."
                        ),
                    ),
                    "specificity": (
                        str,
                        (
                            "Have you narrowed it down to one specific book/franchise/set "
                            "of stories/etc., or are there still multiple possibilities? "
                            "One of: 'one', 'a few', 'several', 'many'."
                        ),
                        ["one", "a few", "several", "many"],
                    ),
                    "confidence_level": (
                        str,
                        (
                            "Your confidence level in this analysis. "
                            "One of: 'high', 'medium', 'low', 'none'."
                        ),
                        ["high", "medium", "low", "none"],
                    ),
                },
            )
        )
        lore_context_possibilities = convo.get_last_reply_dict_field(
            "lore_context_possibilities", "unknown"
        )
        explanation = convo.get_last_reply_dict_field("explanation", "")
        specificity = convo.get_last_reply_dict_field("specificity", "many")
        confidence_level = convo.get_last_reply_dict_field("confidence_level", "none")
        retval = f"""
Inferred lore context: {lore_context_possibilities}
Specificity: {specificity}
Confidence level: {confidence_level}
How we made this determination: {explanation}
"""
        return retval

    def _judge_target_coordinates(
        self,
        targeting_instructions: str,
    ) -> str:
        """Judge how much information leaks about the target coordinates."""
        convo = self._start_convo(targeting_instructions)

        convo.submit_developer_message(
            """
Now that you know the message, your job is to try to determine the target coordinates
*without knowing the lore context*.

The message is supposed to encode target coordinates (like "B6") using the lore context.
But, even without knowing the lore context, the message might still contain hints or clues.

Here are a few examples of what to watch out for:

- The message might directly state coordinates, like "Fire at B6".

- The message might reference positional relationships that are obvious without the lore context.
    For example, the message could instruct you to "fire at the upper left corner", which is A1.
    You can determine that even without knowing the lore context.

- The message might be trying to obfuscate the coordinates using a code, but that code is obvious
    without the lore context. For example, the message could say, "The second letter of the
    alphabet and the number of sides on a cube." Even without knowing the lore context,
    you can figure out that the second letter of the alphabet is 'B' and the number of sides
    on a cube is 6, so the target coordinates are B6. You can determine that without knowing
    the lore context.    

- The message might make references to the lore context, but in a way that still allows you to
    determine the target coordinates. For example, the message could say, "The first letter of
    Aaron's name, and the number of letters in his name." Well, you might not know who "Aaron"
    is or what lore context he's from, but you can still see that the first letter of "Aaron"
    is 'A' and the number of letters in "Aaron" is 5, so the target coordinates are A5.

Etc.

With that in mind, what target coordinates  does this message point to?
If you can't determine the exact coordinates, can you at least narrow it down?

Give a thorough and detailed discussion about what the possible lore contexts are.
Show your reasoning as you go. I'd like to hear your thought process.
"""
        )
        convo.submit(
            json_response=JSONSchemaFormat(
                name="target_coordinates_leakage_analysis",
                description="JSON formalization of the target coordinates leakage analysis.",
                schema={
                    "target_coordinates_possibilities": (
                        str,
                        (
                            "A succinct listing of what the possible target coordinates are, "
                            "based on the message alone. If you can determine it exactly, "
                            "state that. If you can't determine it at all, say 'unknown'."
                        ),
                    ),
                    "explanation": (
                        str,
                        (
                            "A brief but detailed explanation of your reasoning process for "
                            "arriving at these possibilities."
                        ),
                    ),
                    "specificity": (
                        str,
                        (
                            "Have you narrowed it down to one specific target? Or just a few? "
                            "Or are there still several possibilities?"
                            "One of: 'one', 'a few', 'several', 'many'."
                        ),
                        ["one", "a few", "several", "many"],
                    ),
                    "confidence_level": (
                        str,
                        (
                            "Your confidence level in this analysis. "
                            "One of: 'high', 'medium', 'low', 'none'."
                        ),
                        ["high", "medium", "low", "none"],
                    ),
                },
            )
        )
        target_coordinates_possibilities = convo.get_last_reply_dict_field(
            "target_coordinates_possibilities", "unknown"
        )
        explanation = convo.get_last_reply_dict_field("explanation", "")
        specificity = convo.get_last_reply_dict_field("specificity", "many")
        confidence_level = convo.get_last_reply_dict_field("confidence_level", "none")
        retval = f"""
Inferred target coordinates: {target_coordinates_possibilities}
Specificity: {specificity}
Confidence level: {confidence_level}
How we made this determination: {explanation}
"""
        return retval

    def _judge_relative_offsets(
        self,
        targeting_instructions: str,
    ) -> str:
        """Judge whether or not the message is using relative offsets."""
        convo = self._start_convo(targeting_instructions)

        convo.submit_developer_message(
            """
Does this message require you to perform any arithmetic adjustments
to arrive at the target coordinates? For example, does it say something like
"plus two rows down" or "minus one column left"? Does it expect you perform
a division or modulo operation? Does it have you do any calculations
relative to some lore-based reference point (for example: "the number of cats
owned by the kindly old woman, plus two")?
"""
        )
        convo.submit(
            json_response=JSONSchemaFormat(
                name="arithmetic_clue_analysis",
                description="JSON formalization of the arithmetic clue analysis.",
                schema={
                    "uses_arithmetic": (
                        bool,
                        (
                            "True if the message requires arithmetic adjustments to decode "
                            "the target coordinates, False otherwise."
                        ),
                    ),
                    "explanation": (
                        str,
                        (
                            "A brief but detailed explanation of your reasoning process for "
                            "arriving at this determination."
                        ),
                    ),
                },
            )
        )
        uses_arithmetic = convo.get_last_reply_dict_field("uses_arithmetic", False)
        explanation = convo.get_last_reply_dict_field("explanation", "")
        retval = f"""
Uses arithmetic adjustments: {uses_arithmetic}
How we made this determination: {explanation}
"""
        return retval

    def receive_targeting_instructions(
        self,
        targeting_instructions: str,
    ) -> str:
        """
        Try to glean how much information leaks from the given targeting instructions.
        """
        # Execute the three judgment functions in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            lore_leakage_future = executor.submit(
                self._judge_lore_leakage, targeting_instructions
            )
            target_coordinates_future = executor.submit(
                self._judge_target_coordinates, targeting_instructions
            )
            relative_offsets_future = executor.submit(
                self._judge_relative_offsets, targeting_instructions
            )

            # Wait for all tasks to complete and get results
            lore_leakage_analysis = lore_leakage_future.result()
            target_coordinates_analysis = target_coordinates_future.result()
            relative_offsets_analysis = relative_offsets_future.result()

        full_analysis = f"""
LORE LEAKAGE ANALYSIS:
{lore_leakage_analysis}

TARGET COORDINATES ANALYSIS:
{target_coordinates_analysis}

RELATIVE OFFSETS ANALYSIS:
{relative_offsets_analysis}
"""
        return full_analysis
