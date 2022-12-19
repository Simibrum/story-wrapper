"""Class and tools to mirror the Gutenberg corpus in a local database.

    Functions are based on the experiments here -
    https://github.com/benhoyle/gutenberg/blob/master/Get%20List%20of%20Fiction%20Titles.ipynb

"""
from typing import List, Tuple
import logging
import subprocess
import pickle
import gzip
import os
import zipfile
import random
from story_wrapper.data_loaders.parseRDF import readmetadata
from story_wrapper.data_loaders.book import Book

# Get path of current folder
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))


class Gutenberg:
    """Class to mirror the Gutenberg corpus locally."""

    def __init__(self, data_path: str = "~/data/gutenberg", index_path: str = CURRENT_FOLDER):
        """Initialize the class."""
        if "~" in data_path:
            data_path = os.path.expanduser(data_path)
        self.data_path = data_path
        self.index_path = os.path.join(index_path, "indexes", "fiction_index.gz")
        self.fiction_md = None
        # Get indexes of Gutenberg corpus via ParseRDF functions
        logging.info("Indexing Gutenberg corpus.")
        self.metadata = readmetadata()
        logging.info("Indexing complete.")
        logging.info("Number of books in Gutenberg corpus: {}".format(len(self.metadata)))
        # Extract the fiction corpus
        if not os.path.exists(self.index_path):
            logging.info("Extracting fiction corpus.")
            self.parse_fiction()
            logging.info("Adding file paths.")
            self.add_paths()
            logging.info("Saving fiction index.")
            with gzip.open(self.index_path, 'wb') as index_file:
                pickle.dump(self.fiction_md, index_file, protocol=-1)
        else:
            with gzip.open(self.index_path, 'rb') as index_file:
                self.fiction_md = pickle.load(index_file)

    def mirror_gutenberg_corpus(self):
        """Mirror the Gutenberg corpus to a local database."""
        # Based on here - https://roboticape.com/2018/06/26/getting-all-the-books/
        # Run the mirror command
        logging.info("Mirroring Gutenberg corpus to local database.")
        subprocess.call([
            "rsync",
            "-avm",
            "--max-size=10m",
            "--include=\"*/\"",
            "--exclude=\"*-*.zip\"",
            "--exclude=\"*/old/*\"",
            "--include=\"*.zip\"",
            "--exclude=\"*\"",
            "rsync.mirrorservice.org::gutenberg.org",
            self.data_path
        ])

    def parse_fiction(self):
        """Parse the fiction corpus."""
        # Now we iterate to look for fiction
        filtered_md = {}

        for _, book in self.metadata.items():
            fiction = False
            # Iterate through subjects looking for fiction
            for subject in book['subjects']:
                if "fiction" in subject.lower() and "non" not in subject.lower():
                    fiction = True
            # Look for fiction in English
            if fiction and "en" in book['language']:
                filtered_md[int(book['id'])] = book

        logging.info("We have {0} English fiction books in the filtered index".format(len(filtered_md)))
        self.fiction_md = filtered_md
        # pickle.dump(filtered_md, gzip.open("fiction_index.gz", 'wb'), protocol=-1)

    def parse_file_paths(self) -> List[Tuple[str, str]]:
        """Get a list of file paths and book ids."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError("The root path does not exist.")
        logging.info(f"Parsing book paths in {self.data_path}.")
        filelist = []
        for root, dirs, files in os.walk(os.path.expanduser(self.data_path)):
            for file in files:
                if ".zip" in file:
                    book_id = file.split(".")[0]
                    if book_id.isdigit():
                        filelist.append((os.path.join(root, file), book_id))
        if not filelist:
            raise FileNotFoundError("No files found.")
        return filelist

    def add_paths(self):
        """Add paths to the fiction index."""
        # Add paths to the fiction index
        logging.info("Adding paths to fiction index.")
        filelist = self.parse_file_paths()
        for path, bookid in filelist:
            try:
                self.fiction_md[int(bookid)]['path'] = path
            except KeyError:
                logging.debug(f"Book {bookid} not in fiction index.")

    def get_book_text(self, book_id: int) -> str:
        """Get the text of a book from a synced database."""
        book = self.fiction_md.get(book_id, None)
        if book:
            with zipfile.ZipFile(book['path'], 'r') as book_zip:
                # We might want to change this to open the one txt file in the zip
                with book_zip.open('{0}.txt'.format(book['id'])) as txtfile:
                    text = txtfile.read().decode()
        else:
            raise FileNotFoundError
        return text

    def get_book_object(self, book_id: int) -> Book:
        """Get the book object from the index."""
        text = self.get_book_text(book_id)
        return Book(book_id, text)

    def get_ids(self) -> List[int]:
        """Get a list of book ids."""
        return list(self.fiction_md.keys())

    def get_random_book(self) -> Book:
        """Get a random book."""
        book_id = random.choice(self.get_ids())
        return self.get_book_object(book_id)
