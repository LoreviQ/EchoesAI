"""This file contains the fixtures used in the tests for the chatbot module."""

# pylint: disable=redefined-outer-name unused-argument unused-import


from io import BytesIO
from typing import Generator

import pytest

from chatbot import Model, new_model


@pytest.fixture
def model() -> Generator[Model, None, None]:
    """Yields a Model object for testing."""
    model = new_model(mocked=True)
    yield model


@pytest.fixture
def image_stream() -> Generator[BytesIO, None, None]:
    """Return a BytesIO image stream."""
    with open("tests/test_chatbot/test_image.jpg", "rb") as image_file:
        image_stream = BytesIO(image_file.read())
        image_stream.seek(0)  # Reset stream position
        yield image_stream
