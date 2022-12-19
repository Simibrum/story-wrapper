import os
from unittest import TestCase
from unittest.mock import patch
import tempfile
from story_wrapper.data_loaders.gutenberg import Gutenberg, Book
from tests.test_book import TEST_BOOK_TEXT

TEST_MD = {
    1: {
        'title': 'The Irish at the Front',
        'author': 'Michael MacDonagh',
        'language': 'en',
        'date': '2018-06-26',
        'rights': 'Public domain in the USA.',
        'subject': 'Irish -- History -- 20th century -- Fiction',
        'subjects': ['Irish', 'History', '20th century', 'Fiction'],
        'type': 'Text',
        'format': 'application/zip',
        'id': '1',
    },
    2: {
        'title': 'A History of Potatoes',
        'author': 'John Smith',
        'language': 'en',
        'date': '2018-06-26',
        'rights': 'Public domain in the USA.',
        'subject': 'History -- 20th century',
        'subjects': ['History', '20th century', ],
        'type': 'Text',
        'format': 'application/zip',
        'id': '2',
    }
}


class TestGutenberg(TestCase):

    @patch('story_wrapper.data_loaders.gutenberg.readmetadata', return_value=TEST_MD)
    @patch.object(Gutenberg, 'parse_file_paths', return_value=[('test_path', "1")])
    def setUp(self, mock_readmetadata, mock_parse_file_paths) -> None:
        """Set up test."""
        self.test_dir = tempfile.TemporaryDirectory()
        os.mkdir(os.path.join(self.test_dir.name, 'indexes'))
        self.gutenberg = Gutenberg(index_path=self.test_dir.name)

    def test_init(self):
        """Test init."""
        assert self.gutenberg.metadata == TEST_MD
        assert self.gutenberg.fiction_md
        assert self.gutenberg.fiction_md[1] == TEST_MD[1]
        assert 2 not in self.gutenberg.fiction_md
        assert self.gutenberg.fiction_md[1]['path'] == 'test_path'
        assert self.gutenberg.get_ids() == [1]

    @patch.object(Gutenberg, 'get_book_text', return_value=TEST_BOOK_TEXT)
    def test_get_book(self, mock_get_book_text):
        """Get a book."""
        book = self.gutenberg.get_book_object(1)
        assert isinstance(book, Book)
        assert "The Irish at the Front" in book.contents

    def tearDown(self):
        """Close the file, the directory will be removed after the test."""
        self.test_dir.cleanup()
