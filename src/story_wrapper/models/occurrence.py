"""Occurrence model for the story wrapper."""
from spacy.tokens import Span
from story_wrapper.utils import clean_out_punctuation


class Occurrence:
    """An occurrence of a character in a story."""

    def __init__(
            self, location_number: int, spacy_span: Span) -> None:
        """ Initialise occurrence object.

        Args:
            location_number = index number in the list of texts
            spacy_span = span object in spacy - from the ent
        """
        self.location_number = location_number
        self.span = spacy_span
        # Compute a hash ID
        self.id = hash(self)

    def __repr__(self):
        return (
            "<Occurrence - text index: {n}; "
            "span: {s}>"
        ).format(
            n=self.location_number,
            s=self.span
        )

    @property
    def root(self):
        """Wrapper for spacy root of phrase."""
        return self.span.root

    @property
    def root_lemma(self):
        """Get the root lemma for the occurrence."""
        return self.root.lemma_.lower()

    @property
    def non_root_lemma(self):
        """Get the non-root lemmas for the occurrence."""
        return [t.lemma_.lower() for t in self.span if t != self.root and not t.pos_ == 'DET']

    @property
    def text(self):
        """Get the text of the occurrence."""
        span_to_use = self.span
        if self.span[0].pos_ == 'DET':
            span_to_use = self.span[1:]
        # Strip out trailing possessive 's
        text = span_to_use.text
        if text.endswith("'s"):
            text = text[:-2]
        # Check for bundles of punctuation
        text = clean_out_punctuation(text)
        return text



    def as_dict(self) -> dict:
        """Return as a dictionary for output."""
        o_dict = dict()
        o_dict['id'] = self.id
        o_dict['location_number'] = self.location_number
        o_dict['text'] = self.text
        return o_dict
