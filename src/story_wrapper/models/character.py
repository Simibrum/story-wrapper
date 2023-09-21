# -*- coding: utf-8 -*-
from collections import Counter
from spacy.tokens import Token
from story_wrapper.models.occurrence import Occurrence


class Character:
    """Represents a character in a story."""

    def __init__(self):
        """ Initialise object with an entity ID. """
        # Create a new unique hash ID for each instance
        self.id = hash(self)
        # Initialise occurrences list and add span
        self.occurrences = list()
        # Placeholder for canonical name of character
        self.name = None
        self.firstname = None
        self.surname = None
        self.middle_names = []
        self.aliases = []
        # Placeholder for relationships
        self.relationships = dict()

    def __repr__(self) -> str:
        return (
            f"<Character - ID: {self.id}; "
            f"name: '{self.name}'; "
            f"no. of occurrences: {len(self.occurrences)}; "
            f"first name: '{self.firstname}'; "
            f"surname: '{self.surname}'; "
            f"middle names: {self.middle_names}; "
            f"aliases: {self.aliases}>"
        )

    def __len__(self) -> int:
        """Length = number of occurrences."""
        return len(self.occurrences)

    def add_occurrence(self, occurrence: Occurrence) -> list[Occurrence]:
        """Add an occurrence in the form of a spaCy span."""
        self.occurrences.append(occurrence)
        return self.occurrences

    def add_occurrences(self, occurrences: list[Occurrence]) -> list[Occurrence]:
        """ Add a list of occurrences."""
        self.occurrences += occurrences
        return self.occurrences

    def get_text_list(self) -> list[str]:
        """Get a list of all the occurrence text."""
        return [o.text for o in self.occurrences]

    @property
    def first_occurrence(self) -> int:
        """ Return starting index of first occurrence."""
        return min([o.span[0].i for o in self.occurrences])

    def longest_occurrence(self) -> Occurrence:
        """Return the longest occurrence."""
        return max(self.occurrences, key=lambda x: len(x.span))

    @property
    def root_lemma_set(self) -> set:
        """Return the set of root lemma text."""
        return set([o.root_lemma for o in self.occurrences])

    @property
    def non_root_lemma_set(self) -> set:
        """Return the set of non-root lemma text."""
        return set([nrl for o in self.occurrences for nrl in o.non_root_lemma])

    @property
    def main_lemma(self) -> str:
        """Return the main (i.e. most common) lemma."""
        return Counter([o.root_lemma for o in self.occurrences]).most_common(1)[0][0] if len(self) > 0 else None

    def as_dict(self, output_occurrences: bool = True) -> dict:
        """Provide in a dictionary format for output."""
        e_dict = dict()
        e_dict['id'] = self.id
        e_dict['name'] = self.name
        e_dict['no_of_occurrences'] = len(self)
        if output_occurrences:
            e_dict['occurrences'] = [o.as_dict() for o in self.occurrences]
        return e_dict

    def add_relationship(self, second_character_id, links: list[Token]):
        """Add a relationship to another entity."""
        # TODO - will this cause serialisation issues as we are saving tokens? Yes
        # We can possibly just replace with the ordered text string?
        # Get or create key entry for second entity
        relations = self.relationships.setdefault(second_character_id, [])
        # Check links is not already in existing
        if links not in relations:
            relations.append(links)
        # Update with revised list
        self.relationships[second_character_id] = relations
