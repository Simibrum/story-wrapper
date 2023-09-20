"""Test the Character model."""

import pytest
from story_wrapper.models import Character, Occurrence
from spacy.tokens import Span

@pytest.fixture
def sample_occurrence(nlp):
    doc = nlp("John was there.")
    span = Span(doc, 0, 1)
    return Occurrence(0, span)


def test_init():
    character = Character()
    assert isinstance(character.id, int)
    assert character.name is None
    assert character.occurrences == []


def test_repr():
    character = Character()
    repr_str = repr(character)
    assert "Character - ID:" in repr_str
    assert "name: None" in repr_str


def test_len():
    character = Character()
    assert len(character) == 0


def test_add_occurrence(sample_occurrence):
    character = Character()
    character.add_occurrence(sample_occurrence)
    assert len(character) == 1
    assert character.occurrences[0].text == "John"


def test_add_occurrences(sample_occurrence):
    character = Character()
    character.add_occurrences([sample_occurrence, sample_occurrence])
    assert len(character) == 2


def test_get_text_list(sample_occurrence):
    character = Character()
    character.add_occurrence(sample_occurrence)
    assert character.get_text_list() == ["John"]


def test_first_occurrence(nlp, sample_occurrence):
    character = Character()
    character.add_occurrence(sample_occurrence)
    assert character.first_occurrence == 0


def test_longest_occurrence(nlp):
    doc = nlp("John, the tall guy, was there.")
    span1 = Span(doc, 0, 1)
    span2 = Span(doc, 0, 4)
    occurrence1 = Occurrence(0, span1)
    occurrence2 = Occurrence(1, span2)

    character = Character()
    character.add_occurrences([occurrence1, occurrence2])
    assert character.longest_occurrence() == occurrence2


def test_root_lemma_set(sample_occurrence):
    character = Character()
    character.add_occurrence(sample_occurrence)
    assert character.root_lemma_set == {'john'}


def test_non_root_lemma_set(nlp):
    doc = nlp("The tall guy was there.")
    span = Span(doc, 1, 3)
    occurrence = Occurrence(0, span)

    character = Character()
    character.add_occurrence(occurrence)
    assert character.non_root_lemma_set == {'tall'}


def test_main_lemma(sample_occurrence):
    character = Character()
    character.add_occurrence(sample_occurrence)
    assert character.main_lemma == 'john'


def test_as_dict(sample_occurrence):
    character = Character()
    character.add_occurrence(sample_occurrence)
    character_dict = character.as_dict()

    assert character_dict['id'] == character.id
    assert character_dict['name'] == character.name
    assert character_dict['no_of_occurrences'] == 1
    assert 'occurrences' in character_dict
