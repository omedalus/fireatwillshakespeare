"""Ally logic for receiving player commands."""

from typing import Optional

import openai

from models.entities import Coordinates

from utils.gpt import GptConversation


class Ally:
    """The friendly artillery team that decodes player messages."""

    def __init__(self, openai_client: openai.Client) -> None:
        self.lore_context: Optional[str] = None
        self.openai_client = openai_client
        # TODO: Retain a message history for better contextual understanding

    def establish_lore_context(self, lore_context: str) -> str:
        """Store the shared lore context provided by the player."""
        self.lore_context = lore_context
        return lore_context

    def receive_message(self, message: str) -> Coordinates:
        """Decode an obfuscated message into target coordinates."""
        if not self.lore_context:
            raise ValueError("Lore context not set. Call establish_lore_context first.")

        convo = GptConversation()

        # TODO: We'll put AI here. For now, the ally always fires at A1.
        print("In light of", self.lore_context)
        print("We always fire on A1, sir!")
        return Coordinates.from_string("A1")
