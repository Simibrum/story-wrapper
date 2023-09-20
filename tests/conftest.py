"""Common fixtures for tests."""

import pytest
from story_wrapper.config_spacy import NLPService


@pytest.fixture(scope='session')
def nlp():
    return NLPService().get_nlp()
