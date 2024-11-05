"""
This module contains functions for generating comments.
"""

import database as db

from .model import Model


def generate_comment(model: Model, char_id: int) -> None:
    """Full logic for generating a comment."""
    # Step 1 - provide character with posts and ask them to choose one to comment on

    # Step 2 - assemble a log of interactions between the character who made the post and the current character
    # Step 3 - generate a comment based on the log
