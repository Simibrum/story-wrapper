"""Wrapper for a longer form document built of spaCy docs."""
from typing import List, Optional, Tuple, Union
from story_wrapper.config_spacy import nlp_service
from spacy.tokens import Doc, Span, Token


def clean_text(text: List[str]) -> List[str]:
    """Clean text ready for NLP."""
    pass


class Story:
    """Class definition for longer form story."""

    def __init__(self, text: Union[List[str], str], process_on_load: bool = True) -> None:
        """Initialise story object."""
        # Convert to default list even if single string
        if isinstance(text, str):
            self.text = [text]
        self.text = text
        if process_on_load:
            self.docs = self.process()
        else:
            self.docs = []

    def __len__(self) -> int:
        """Return the length of the story."""
        return len(self.text)

    def __getitem__(self, index: int) -> str:
        """Return the text of the paragraph at the given index."""
        return self.text[index]

    def __iter__(self) -> str:
        """Return an iterator over the paragraphs."""
        return iter(self.text)

    def __contains__(self, item: str) -> bool:
        """Return True if the item is in the story."""
        return item in self.text

    def __repr__(self) -> str:
        """Return a string representation of the story."""
        return f"Story({self.text})"

    def __str__(self) -> str:
        """Return a string representation of the story."""
        return f"Story({self.text})"

    def process(self) -> List[Doc]:
        """Process the story and return a list of spacy docs."""
        nlp = nlp_service.get_nlp()
        doc_generator = nlp.pipe(
            self.text
        )
        return list(doc_generator)
    