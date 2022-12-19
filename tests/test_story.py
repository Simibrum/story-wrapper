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
