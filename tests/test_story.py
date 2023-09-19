"""Test file for story object."""
from unittest import TestCase
from tests.test_book import Book, TEST_BOOK_TEXT
from src.story_wrapper.models.story import Story


class TestStory(TestCase):
    def test_story(self):
        """Test story."""
        book = Book(1, TEST_BOOK_TEXT[0:40000])
        assert book.paragraphs
        story = Story(book.paragraphs)
        assert story.docs
        characters = story.characters()
        assert characters == ['MONS', 'John French', 'De Freyne', 'Douglas Haig', 'Horace Smith-Dorrien']
        assert len(story) == 5
        assert story.count_characters() == {
            'MONS': 1, 'John French': 1, 'De Freyne': 1, 'Douglas Haig': 1, 'Horace Smith-Dorrien': 1}
