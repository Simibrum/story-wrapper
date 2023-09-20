"""Test the occurrence object."""

from story_wrapper.config_spacy import NLPService
import pytest
from story_wrapper.models import Occurrence


def test_initialization(nlp):
    doc = nlp("This is a test sentence.")
    span = doc[3:5]  # Span for "test sentence"
    occurrence = Occurrence(0, span)
    assert occurrence.location_number == 0
    assert occurrence.span.text == "test sentence"


def test_repr(nlp):
    doc = nlp("Another test sentence.")
    span = doc[1:3]  # Span for "test sentence"
    occurrence = Occurrence(1, span)
    assert repr(occurrence).startswith("<Occurrence - text index: 1;")


def test_root(nlp):
    doc = nlp("A quick brown fox.")
    span = doc[2:4]  # Span for "brown fox"
    occurrence = Occurrence(0, span)
    assert occurrence.root.text == "fox"


def test_root_lemma(nlp):
    doc = nlp("Jumps over.")
    span = doc[0:1]  # Span for "Jumps"
    occurrence = Occurrence(0, span)
    assert occurrence.root_lemma == "jump"


def test_non_root_lemma(nlp):
    doc = nlp("The quick brown fox.")
    span = doc[2:4]  # Span for "brown fox"
    occurrence = Occurrence(0, span)
    assert "brown" in occurrence.non_root_lemma


def test_text(nlp):
    doc = nlp("The quick brown fox.")
    span = doc[0:3]  # Span for "The quick brown"
    occurrence = Occurrence(0, span)
    assert occurrence.text == "quick brown"


def test_as_dict(nlp):
    doc = nlp("Another test sentence.")
    span = doc[1:3]  # Span for "test sentence"
    occurrence = Occurrence(1, span)
    as_dict = occurrence.as_dict()
    assert as_dict['location_number'] == 1
    assert as_dict['text'] == "test sentence"
    assert 'id' in as_dict
