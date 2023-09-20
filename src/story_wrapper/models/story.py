"""Wrapper for a longer form document built of spaCy docs."""
import re
from typing import List, Tuple, Union, Iterator
from itertools import combinations
from collections import Counter, defaultdict
from spacy.tokens import Doc, Span
from nicknames import NickNamer
from story_wrapper.config_spacy import nlp_service
from story_wrapper.models.occurrence import Occurrence
from story_wrapper.models.character import Character

nn = NickNamer()

# Regex for whitespace
WHITESPACE = re.compile(r" ?(?:\t|\r|\n  +|\u2007+|\u2003+|\ue89e+|\u2062+|\ue8a0+) ?")


def remove_excess_whitespace(text: str) -> str:
    """Remove excess whitespace such as tabs and multiple spaces that causes parsing errors."""
    return re.sub(WHITESPACE, " ", text)


def clean_text(text: str) -> str:
    """Clean text ready for NLP."""
    # Replace new lines and carriage returns with spaces & filter out double spaces
    return remove_excess_whitespace(text).strip()


def merge_characters_by_alias(main_character: Character, character_to_merge: Character) -> Character:
    """Merge two characters and return merged Character object."""
    main_character.add_occurrences(character_to_merge.occurrences)
    main_character.aliases.append(character_to_merge.firstname)
    return main_character


def filter_relevant_character_combinations(characters: list[Character]) -> list:
    """
    Filter out combinations of candidates where no tokens match.

    Args:
    - characters: a list of potential characters in the Character object form.

    Returns:
    - list: A filtered list of relevant combinations.
    """
    relevant_combinations = []
    excluded_pos = ["DET", "PART", "ADP"]

    # Generate all combinations of 2 candidates
    for candidate1, candidate2 in combinations(characters, 2):
        span1 = candidate1.occurrences[0].span
        span2 = candidate2.occurrences[0].span

        tokens1 = {token.lower_ for token in span1 if token.pos_ not in excluded_pos}
        tokens2 = {token.lower_ for token in span2 if token.pos_ not in excluded_pos}

        # Check if there are any common tokens
        if tokens1.intersection(tokens2):
            relevant_combinations.append((candidate1, candidate2))

    return relevant_combinations


class Story:
    """Class definition for longer form story."""

    def __init__(self, text: Union[List[str], str], process_on_load: bool = True) -> None:
        """Initialise story object."""
        # Convert to default list even if single string
        if isinstance(text, str):
            self.text = [text]
        self.text = [clean_text(t) for t in text]
        # Initialise list of character occurrences
        self.occurrences = []
        # Initialise set of characters
        self.characters = {}
        # Initialise set of potential characters
        self.potential_characters = {}
        # Initialise list of docs
        self.docs = []
        # Initialise list of names to process
        self.names_to_process = []
        # Process the story
        if process_on_load:
            self.docs = self.process()
            self.process_occurrences()
            self.names_to_process = list(self.get_occurrences_by_text().keys())

    def __len__(self) -> int:
        """Return the length of the story."""
        return len(self.text)

    def __getitem__(self, index: int) -> str:
        """Return the text of the paragraph at the given index."""
        return self.text[index]

    def __iter__(self) -> Iterator[str]:
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

    def people_list(self) -> List[str]:
        """Return a list of characters in the story."""
        string_occurrences = []
        for doc in self.docs:
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    string_occurrences.append(ent.text)
        return string_occurrences

    def count_characters(self) -> Counter:
        """Return a counter of characters in the story."""
        return Counter(self.people_list())

    def process_occurrences(self):
        """Process the occurrences of characters in the story."""
        # Process the story
        for i, doc in enumerate(self.docs):
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    self.occurrences.append(Occurrence(i, ent))
        return self.occurrences

    def get_occurrences_by_text(self) -> dict:
        """Return a dictionary of occurrences by text."""
        occurrences_by_text = defaultdict(list)
        for o in self.occurrences:
            occurrences_by_text[o.text.lower()].append(o)
        return occurrences_by_text

    def get_single_token_candidates(self) -> list:
        """Return a list of strings that have multiple tokens."""
        return [
            k for k, v in self.get_occurrences_by_text().items()
            if len(v[0].span) == 1
        ]

    def get_multiple_token_candidates(self) -> list:
        """Return a list of strings that have multiple tokens."""
        return [
            k for k, v in self.get_occurrences_by_text().items()
            if len(v[0].span) > 1
        ]

    def populate_name_candidates(self) -> Tuple[set, set]:
        """Populate dictionaries for first and last name candidates."""
        occurrences_by_text = self.get_occurrences_by_text()
        potential_first_names = set()
        potential_surnames = set()
        for name in self.get_multiple_token_candidates():
            span = occurrences_by_text[name][0].span
            first_name = span[0] if span[0].pos_ != "DET" else span[1]
            last_name = span[-1] if span[-1].text != "'s" else span[-2]
            potential_first_names.add(first_name.lower_)
            potential_surnames.add(last_name.lower_)
        return potential_first_names, potential_surnames

    def get_potential_characters(self) -> dict[Character]:
        """Return a dict of potential characters."""
        occurrences_by_text = self.get_occurrences_by_text()
        for candidate in self.get_multiple_token_candidates():
            new_character = Character()
            new_character.name = candidate
            new_character.add_occurrences(occurrences_by_text[candidate])
            splits = candidate.split()
            if len(splits) > 1:
                new_character.firstname = splits[0]
                new_character.surname = splits[-1]
                if len(splits) > 2:
                    new_character.middle_names = splits[1:-1]
            self.potential_characters[new_character.id] = new_character
            # Remove from names to process
            self.names_to_process.remove(candidate)
        return self.potential_characters

    def merge_by_nicknames(self) -> dict:
        """Merge potential characters by nicknames."""
        if not self.potential_characters:
            self.get_potential_characters()
        characters = self.potential_characters.copy()
        characters_as_list = list(characters.values())
        relevant_combinations = filter_relevant_character_combinations(characters_as_list)
        for candidate1, candidate2 in relevant_combinations:
            if candidate2.firstname in nn.nicknames_of(candidate1.firstname):
                merge_characters_by_alias(candidate1, candidate2)
                del characters[candidate2.id]
            if candidate1.firstname in nn.nicknames_of(candidate2.firstname):
                merge_characters_by_alias(candidate2, candidate1)
                del characters[candidate1.id]
        self.potential_characters = characters
        return self.potential_characters

    def process_characters(self) -> dict:
        """Process the characters in the story."""
        self.merge_by_nicknames()
        return self.potential_characters

    def merge_occurrences(self, potential_matches: dict, backward_matches: dict):
        """Merge occurrences based on matches."""
        for char_id, single_names in potential_matches.items():
            for single_name in single_names:
                if len(potential_matches[char_id]) == 1 and len(backward_matches[single_name]) == 1:
                    character = self.potential_characters[char_id]
                    single_occurrences = self.get_occurrences_by_text()[single_name]
                    character.add_occurrences(single_occurrences)
                    self.names_to_process.remove(single_name)

    def match_single_firstname_characters(self):
        """Match occurrences to characters based on unique firstname matches."""
        potential_matches = defaultdict(list)
        backward_matches = defaultdict(list)

        for character in self.potential_characters.values():
            for single_name in self.get_single_token_candidates():
                if single_name == character.firstname or single_name in nn.nicknames_of(character.firstname):
                    potential_matches[character.id].append(single_name)
                    backward_matches[single_name].append(character.id)

        self.merge_occurrences(potential_matches, backward_matches)

    def match_single_surname_characters(self):
        """Match occurrences to characters based on unique surname matches."""
        potential_matches = defaultdict(list)
        backward_matches = defaultdict(list)

        for character in self.potential_characters.values():
            for single_name in self.get_single_token_candidates():
                if single_name == character.surnname:
                    potential_matches[character.id].append(single_name)
                    backward_matches[single_name].append(character.id)

        self.merge_occurrences(potential_matches, backward_matches)
        # TODO add tests for this and above
