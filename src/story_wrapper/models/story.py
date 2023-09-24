"""Wrapper for a longer form document built of spaCy docs."""
import re
from typing import List, Tuple, Union, Iterator
from itertools import combinations
from collections import Counter, defaultdict
from spacy.tokens import Doc, Span
from nicknames import NickNamer

from story_wrapper.init_logger import logger
from story_wrapper.config_spacy import nlp_service
from story_wrapper.models.occurrence import Occurrence
from story_wrapper.models.character import Character
from story_wrapper.utils import clean_out_punctuation

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

        tokens1 = {clean_out_punctuation(token.lower_) for token in span1 if token.pos_ not in excluded_pos}
        tokens2 = {clean_out_punctuation(token.lower_) for token in span2 if token.pos_ not in excluded_pos}

        # Check if there are any common tokens
        if tokens1.intersection(tokens2) or tokens2.intersection(tokens1):
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

    def get_main_characters(self, n: int = None) -> List[str]:
        """Return the top n characters in the story."""
        char_list = self.potential_characters.values()
        if not n:
            n = len(char_list)
        sorted_chars = sorted(char_list, key=lambda x: len(x), reverse=True)
        return [c for c in sorted_chars[:n]]

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

    def merge_by_plural(self) -> dict:
        """Merge potential characters by checking for plurals."""
        if not self.potential_characters:
            self.get_potential_characters()
        characters = self.potential_characters.copy()
        characters_as_list = list(characters.values())
        relevant_combinations = filter_relevant_character_combinations(characters_as_list)
        for candidate1, candidate2 in relevant_combinations:
            # Check if we have a first name match
            if candidate1.firstname == candidate2.firstname:
                # Check if one of the surname tokens is a plural
                # We'll need to go back to the original spacy span to check this
                span1 = candidate1.occurrences[0].span
                span2 = candidate2.occurrences[0].span
                if span1[-1].tag_ == "NNPS":
                    # Check whether the last tokens match without an "s" on span1[-1]
                    if candidate1.surname[:-1] == candidate2.surname:
                        # If so, merge and delete candidate2
                        candidate2.add_occurrences(candidate1.occurrences)
                        del characters[candidate1.id]
                elif span2[-1].tag_ == "NNPS":
                    # Check whether the last tokens match without an "s" on span1[-1]
                    if candidate2.surname[:-1] == candidate1.surname:
                        candidate1.add_occurrences(candidate2.occurrences)
                        del characters[candidate2.id]
        self.potential_characters = characters
        return self.potential_characters

    def merge_by_initial(self) -> dict:
        """Merge potential characters by checking for initials."""
        if not self.potential_characters:
            self.get_potential_characters()
        characters = self.potential_characters.copy()
        characters_as_list = list(characters.values())
        relevant_combinations = filter_relevant_character_combinations(characters_as_list)
        matches = []
        for candidate1, candidate2 in relevant_combinations:
            # Check if we have a surname name match
            if candidate1.surname == candidate2.surname and candidate1.firstname[0] == candidate2.firstname[0]:
                if "." in candidate1.firstname and len(candidate1.firstname) < 3:
                    matches.append((candidate2, candidate1))
                elif "." in candidate2.firstname and len(candidate2.firstname) < 3:
                    matches.append((candidate1, candidate2))
        # If only a single match (i.e. no ambiguity) - merge
        if len(matches) == 1:
            main, to_merge_in = matches[0]
            merge_characters_by_alias(main, to_merge_in)
            del characters[to_merge_in.id]
        self.potential_characters = characters
        return self.potential_characters

    def process_characters(self) -> dict:
        """Process the characters in the story."""
        self.merge_by_plural()
        self.merge_by_initial()
        self.merge_by_nicknames()
        self.match_single_name_characters("surname")
        self.match_single_name_characters("firstname")
        self.add_characters_from_single_strings()
        return self.potential_characters

    def merge_occurrences(self, potential_matches: dict, backward_matches: dict):
        """Merge occurrences based on matches."""
        for char_id, single_names in potential_matches.items():
            for single_name in single_names:
                if len(potential_matches[char_id]) == 1 and len(backward_matches[single_name]) == 1:
                    character = self.potential_characters[char_id]
                    single_occurrences = self.get_occurrences_by_text()[single_name]
                    character.add_occurrences(single_occurrences)
                    if single_name in self.names_to_process:
                        self.names_to_process.remove(single_name)

    def match_single_name_characters(
            self,
            name_attribute: str
    ) -> None:
        """
        Match occurrences to characters based on unique name matches.

        Args:
            name_attribute (str): The attribute of the Character object to consider for matching.
            Can be 'firstname' or 'surname'.

        """
        if name_attribute not in ['firstname', 'surname']:
            raise ValueError(f"Invalid name_attribute: {name_attribute}")

        potential_matches = defaultdict(list)
        backward_matches = defaultdict(list)

        for character in self.potential_characters.values():
            for single_name in self.get_single_token_candidates():
                if single_name == getattr(character, name_attribute):
                    potential_matches[character.id].append(single_name)
                    backward_matches[single_name].append(character.id)

        self.merge_occurrences(potential_matches, backward_matches)

        # TODO add tests for this and above
        # TODO we might want to save the forward and backward matches for later
        # These could be used for disambiguation

    def add_characters_from_single_strings(self):
        """Add characters from single strings after initial population."""
        processed_names = []
        characters = self.potential_characters
        # Iterate over unmatched string names
        for name in self.names_to_process:
            character_match = defaultdict(list)
            # Try to match with existing characters
            for char in characters.values():
                existing_names = {char.surname, char.firstname} | {alias for alias in char.aliases}
                # Add also potential nicknames
                existing_names.update(nn.nicknames_of(char.firstname))
                # Also check for plurals
                # Check that existing surname is not a plural then add the plural form
                if not char.surname.endswith("s"):
                    if not char.occurrences[0].span[-1].tag_ == "NNPS":
                        # Add with an s to compare
                        existing_names.add(char.surname + "s")
                logger.debug(f"Comparing: '{name}' to {existing_names}")
                if name in existing_names:
                    character_match[name].append(char.id)
            logger.debug(f"Character matches: {character_match[name]}")
            if len(character_match[name]) == 0:
                logger.debug(f"{name} has no matches with existing potential characters")
                # If no matches, create a new character
                new_character = Character()
                new_character.name = name
                new_character.add_occurrences(self.get_occurrences_by_text()[name])
                self.potential_characters[new_character.id] = new_character
                processed_names.append(name)
            else:
                logger.debug(f"{name} has matches: {[characters[c] for c in character_match[name]]}")
        # Mark processed names as processed
        for name in processed_names:
            self.names_to_process.remove(name)
