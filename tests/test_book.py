"""Code to test gutenberg book processing."""
from unittest import TestCase
from unittest.mock import patch
from story_wrapper.data_loaders.book import Book

# Mock the get_book function
with open("test_data_book.txt", errors='ignore') as f:
    TEST_BOOK_TEXT = f.read()


class TestBook(TestCase):
    def test_get_text(self):
        book = Book(1, TEST_BOOK_TEXT)
        assert book.contents == TEST_BOOK_TEXT
        # print(book.lines[20:30])
        # print(book.contents.split('\n\n'))
        assert book.end_location
        assert book.heading_locations == [760, 1172, 1422, 1679, 1971, 2412, 2724, 2937, 3273, 3771, 4047, 4586, 5145]
        assert [book.lines[loc] for loc in book.heading_locations] == [
            'CHAPTER I', 'CHAPTER II', 'CHAPTER III', 'CHAPTER IV', 'CHAPTER V', 'CHAPTER VI', 'CHAPTER VII',
            'CHAPTER VIII', 'CHAPTER IX', 'CHAPTER X', 'CHAPTER XI', 'CHAPTER XII',
            "End of Project Gutenberg's The Irish at the Front, by Michael MacDonagh"
        ]
        assert len(book.paragraphs) == 305


