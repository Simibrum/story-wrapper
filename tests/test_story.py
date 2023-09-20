"""Test file for story object."""
from unittest.mock import Mock
from collections import defaultdict
from typing import Tuple, List
from tests.test_book import Book, TEST_BOOK_TEXT
from story_wrapper.models.story import Story
from story_wrapper.models.occurrence import Occurrence
from story_wrapper.models.character import Character


def test_story():
    """Test story."""
    book = Book(1, TEST_BOOK_TEXT[0:40000])
    assert book.paragraphs
    story = Story(book.paragraphs)
    assert story.docs
    characters = story.people_list()
    assert characters == ['MONS', 'John French', 'De Freyne', 'Douglas Haig', 'Horace Smith-Dorrien']
    assert len(story) == 5
    assert story.count_characters() == {
        'MONS': 1, 'John French': 1, 'De Freyne': 1, 'Douglas Haig': 1, 'Horace Smith-Dorrien': 1}


# Create mock doc and ent objects
mock_ent1 = Mock()
mock_ent1.label_ = "PERSON"

mock_ent2 = Mock()
mock_ent2.label_ = "GPE"  # Not a person

mock_doc = Mock()
mock_doc.ents = [mock_ent1, mock_ent2]


def test_process_occurrences():
    # Arrange
    story = Story([])
    story.docs = [mock_doc]
    story.occurrences = []

    # Act
    occurrences = story.process_occurrences()

    # Assert
    assert len(occurrences) == 1
    assert isinstance(occurrences[0], Occurrence)
    assert occurrences[0].location_number == 0


def test_get_occurrences_by_text():
    # Mock Occurrence objects
    mock_occ1 = Mock()
    mock_occ1.text.lower.return_value = 'john'

    mock_occ2 = Mock()
    mock_occ2.text.lower.return_value = 'john'

    mock_occ3 = Mock()
    mock_occ3.text.lower.return_value = 'sarah'

    # Arrange
    story = Story([])
    story.occurrences = [mock_occ1, mock_occ2, mock_occ3]

    expected_output = defaultdict(list, {'john': [mock_occ1, mock_occ2], 'sarah': [mock_occ3]})

    # Act
    occurrences_by_text = story.get_occurrences_by_text()

    # Assert
    assert occurrences_by_text == expected_output


def test_get_multiple_token_candidates():
    # Mock Occurrence objects
    mock_occ1 = Mock()
    mock_occ1.text.lower.return_value = 'john'
    mock_occ1.span = ['john']

    mock_occ2 = Mock()
    mock_occ2.text.lower.return_value = 'john doe'
    mock_occ2.span = ['john', 'doe']

    mock_occ3 = Mock()
    mock_occ3.text.lower.return_value = 'sarah connor'
    mock_occ3.span = ['sarah', 'connor']

    # Arrange
    story = Story([])  # Initialize your Story object, add required args if needed
    story.occurrences = [mock_occ1, mock_occ2, mock_occ3]

    expected_output = ['john doe', 'sarah connor']

    # Act
    multiple_token_candidates = story.get_multiple_token_candidates()

    # Assert
    assert multiple_token_candidates == expected_output


# Mock Spacy Token objects
def mock_token(text: str, pos: str = None) -> Mock:
    mock_t = Mock()
    mock_t.lower_ = text.lower()
    mock_t.pos_ = pos
    mock_t.text = text
    return mock_t


# Mock Occurrence objects
def mock_occurrence(name: str, span_tokens: Tuple[Tuple]) -> Mock:
    mock_occ = Mock()
    mock_occ.text.lower.return_value = name.lower()
    mock_occ.span = [mock_token(token, pos) for token, pos in span_tokens]
    return mock_occ


def test_populate_name_candidates():
    # Arrange
    story = Story([])
    story.occurrences = [
        mock_occurrence("John Doe", (("John", None),("Doe", None))),
        mock_occurrence("Sarah Connor", (("Sarah", None), ("Connor", None))),
        mock_occurrence("Captain Ahab's", (("Captain", None), ("Ahab", None), ("'s", "PART"))),
        mock_occurrence("The Master", (("The", "DET"), ("Master", None))),
    ]

    expected_first_names = {'john', 'sarah', 'captain', 'master'}
    expected_surnames = {'doe', 'connor', 'ahab', 'master'}

    # Act
    potential_first_names, potential_surnames = story.populate_name_candidates()

    # Assert
    assert potential_first_names == expected_first_names
    assert potential_surnames == expected_surnames


def test_get_potential_characters():
    # Arrange
    story = Story([])
    story.occurrences = [
        mock_occurrence("John Doe", (("John", None), ("Doe", None))),
        mock_occurrence("Sarah Connor", (("Sarah", None), ("Connor", None))),
        mock_occurrence("Arthur Conan Doyle", (("Arthur", None), ("Conan", None), ("Doyle", None)))
    ]

    expected_characters = [
        {"name": "john doe", "first_name": "john", "surname": "doe", "middle_names": []},
        {"name": "sarah connor", "first_name": "sarah", "surname": "connor", "middle_names": []},
        {"name": "arthur conan doyle", "first_name": "arthur", "surname": "doyle", "middle_names": ["conan"]},
    ]

    # Act
    potential_characters: List[Character] = story.get_potential_characters()
    actual_characters = []
    for char in potential_characters:
        actual_characters.append({
            "name": char.name,
            "first_name": char.firstname,
            "surname": char.surname,
            "middle_names": char.middle_names
        })

    # Assert
    assert actual_characters == expected_characters
