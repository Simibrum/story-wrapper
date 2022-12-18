from unittest import TestCase
from src.story_wrapper.data_loaders.gutenberg import parse_file_paths


class Test(TestCase):
    def test_parse_file_paths(self):
        filelist = parse_file_paths()
        assert filelist
