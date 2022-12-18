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
from src.story_wrapper.data_loaders.parseRDF import readmetadata


def index_gutenberg_corpus():
    """Index the Gutenberg corpus."""
    # Use the parseRDF module to index the Gutenberg corpus
    logging.info("Indexing Gutenberg corpus.")
    md = readmetadata()
    logging.info("Indexing complete.")
    logging.info("Number of books in Gutenberg corpus: {}".format(len(md)))
    return md


def parse_fiction():
    """Parse the fiction corpus."""
    md = index_gutenberg_corpus()
    # Now we iterate to look for fiction
    filtered_md = {}

    for _, book in md.items():
        fiction = False
        # Iterate through subjects looking for fiction
        for subject in book['subjects']:
            if "fiction" in subject.lower() and "non" not in subject.lower():
                fiction = True
        # Look for fiction in English
        if fiction and "en" in book['language']:
            filtered_md[book['id']] = book

    logging.info("We have {0} English fiction books in the filtered index".format(len(filtered_md)))
    pickle.dump(filtered_md, gzip.open("fiction_index.gz", 'wb'), protocol=-1)


def parse_file_paths(root_path: str = "~/data/gutenberg") -> List[Tuple[str, str]]:
    """Get a list of file paths and book ids."""
    if not os.path.exists(os.path.expanduser(root_path)):
        raise FileNotFoundError("The root path does not exist.")
    logging.info(f"Parsing book paths in {root_path}.")
    filelist = []
    for root, dirs, files in os.walk(os.path.expanduser(root_path)):
        for file in files:
            if ".zip" in file:
                book_id = file.split(".")[0]
                if book_id.isdigit():
                    filelist.append((os.path.join(root, file), book_id))
    if not filelist:
        raise FileNotFoundError("No files found.")
    return filelist


def add_paths(root_path: str = "~/data/gutenberg"):
    """Add paths to the fiction index."""
    # Add paths to the fiction index
    logging.info("Adding paths to fiction index.")
    with gzip.open("fiction_index.gz", 'rb') as index_file:
        fiction_index = pickle.load(index_file)
    # TODO - revise as a class with path as init parameter
    filelist = parse_file_paths(root_path)
    for path, bookid in filelist:
        book = fiction_index.get(int(bookid), None)
        try:
            fiction_index[int(bookid)]['path'] = path
        except KeyError:
            pass
    with gzip.open("fiction_index.gz", 'wb') as index_file:
        pickle.dump(fiction_index, index_file, protocol=-1)


def mirror_gutenberg_corpus():
    """Mirror the Gutenberg corpus to a local database."""
    # Based on here - https://roboticape.com/2018/06/26/getting-all-the-books/
    # Run the mirror command
    logging.info("Mirroring Gutenberg corpus to local database.")
    path = input("Please enter the path for the Gutenberg corpus (return to use default '~/data/gutenberg'): ")
    if not path:
        path = os.path.expanduser("~/data/gutenberg")
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
        path
    ])


def parse_gutenberg_corpus():
    """Parse the Gutenberg corpus."""
    # Parse the Gutenberg corpus
    logging.info("Parsing Gutenberg corpus.")
    if not os.path.exists("fiction_index.gz"):
        parse_fiction()
        add_paths()


def get_book(book_id):
    """Get the text of a book from a synced database."""
    fiction_dict = pickle.load(gzip.open("fiction_index.gz", 'rb'))
    book = fiction_dict.get(book_id, None)
    if book:
        with zipfile.ZipFile(book['path'], 'r') as book_zip:
            # We might want to change this to open the one txt file in the zip
            with book_zip.open('{0}.txt'.format(book['id'])) as txtfile:
                text = txtfile.read().decode()
    else:
        raise FileNotFoundError
    return text
