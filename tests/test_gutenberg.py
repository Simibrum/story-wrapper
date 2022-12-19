import os
from unittest import TestCase
from unittest.mock import patch
import tempfile
from story_wrapper.data_loaders.gutenberg import Gutenberg

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

    def setUp(self) -> None:
        """Set up test."""
        self.test_dir = tempfile.TemporaryDirectory()
        os.mkdir(os.path.join(self.test_dir.name, 'indexes'))

    @patch('story_wrapper.data_loaders.gutenberg.readmetadata', return_value=TEST_MD)
    @patch.object(Gutenberg, 'parse_file_paths', return_value=[('test_path', "1")])
    def test_init(self, mock_readmetadata, mock_parse_file_paths):
        """Test init."""
        gutenberg = Gutenberg(index_path=self.test_dir.name)
        assert gutenberg.metadata == TEST_MD
        assert gutenberg.fiction_md
        print(gutenberg.fiction_md)
        assert gutenberg.fiction_md[1] == TEST_MD[1]
        assert 2 not in gutenberg.fiction_md
        assert gutenberg.fiction_md[1]['path'] == 'test_path'

    def tearDown(self):
        """Close the file, the directory will be removed after the test."""
        self.test_dir.cleanup()
