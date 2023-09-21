"""Miscellaneous general utilities."""
import os
import re
from hashlib import blake2b


def create_hash_id(text: str, with_salt: bool = True) -> str:
    """Create a unique salted hash string for passed text. Each iteration gives a different ID."""
    if with_salt:
        salt = os.urandom(blake2b.SALT_SIZE)
        hash_id = blake2b(digest_size=10, salt=salt)
    else:
        hash_id = blake2b(digest_size=10)
    hash_id.update(text.encode())
    return hash_id.hexdigest()


def clean_out_punctuation(text: str) -> str:
    """Clean out punctuation from the text."""
    punctuation_splits = re.split(r'[^a-zA-Z0-9. ]{2,}', text)
    if len(punctuation_splits) > 1:
        # TODO - we might want to look for the longest if the punctuation bundle is not at the end
        text = punctuation_splits[0]
    return text
