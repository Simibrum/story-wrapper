"""Wrapper for a longer form document built of spaCy docs."""
from typing import List, Optional, Tuple, Union

from spacy.tokens import Doc, Span, Token


class Story:
    """Class definition for longer form story."""

    def __init__(self, text: Union[List[str], str]) -> None:
        """Initialise story object."""
        # Convert to default list even if single string
        if isinstance(text, str):
            self.text = [text]
        self.text = text
    