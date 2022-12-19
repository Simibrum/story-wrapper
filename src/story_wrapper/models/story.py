"""Wrapper for a longer form document built of spaCy docs."""
import re
from typing import List, Optional, Tuple, Union
from collections import Counter
from story_wrapper.config_spacy import nlp_service
from spacy.tokens import Doc, Span, Token

# Regex for whitespace
WHITESPACE = re.compile(r" ?(?:\t|\r|\n  +|\u2007+|\u2003+|\ue89e+|\u2062+|\ue8a0+) ?")


def remove_excess_whitespace(text: str) -> str:
    """Remove excess whitespace such as tabs and multiple spaces that causes parsing errors."""
    return re.sub(WHITESPACE, " ", text)


def clean_text(text: str) -> str:
    """Clean text ready for NLP."""
    # Replace new lines and carriage returns with spaces & filter out double spaces
    return remove_excess_whitespace(text).strip()


class Story:
    """Class definition for longer form story."""

    def __init__(self, text: Union[List[str], str], process_on_load: bool = True) -> None:
        """Initialise story object."""
        # Convert to default list even if single string
        if isinstance(text, str):
            self.text = [text]
        self.text = [clean_text(t) for t in text]
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

    def unique_entities(self) -> Tuple[set, List[Span]]:
        """Return a list of unique entities in the story."""
        entities = set()
        entity_spans = []
        for doc in self.docs:
            for ent in doc.ents:
                if ent.text not in entities:
                    entities.add(ent.text)
                    entity_spans.append(ent)
        return entities, entity_spans

    def characters(self) -> List[Span]:
        """Return a list of characters in the story."""
        characters = []
        for doc in self.docs:
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    characters.append(ent.text)
        return characters

    def count_characters(self) -> Counter:
        """Return a counter of characters in the story."""
        return Counter(self.characters())
