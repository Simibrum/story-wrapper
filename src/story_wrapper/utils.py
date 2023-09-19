"""Miscellaneous general utilities."""
import os
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
