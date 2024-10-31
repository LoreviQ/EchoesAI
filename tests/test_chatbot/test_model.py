"""This file contains the tests for the chatbot/model.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import importlib
from typing import Generator

import pytest
from transformers import Pipeline

from chatbot import Model, new_model
from tests.test_database_old.test_main import db_init

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
model_module = importlib.import_module("chatbot.model")
ModelMocked = getattr(model_module, "ModelMocked")
ModelActual = getattr(model_module, "ModelActual")


@pytest.fixture
def model(db_init: str) -> Generator[Model, None, None]:
    """Yields a Model object for testing."""
    model = new_model(mocked=True)
    yield model


def test_new_model_mocked() -> None:
    """Test the new_model function when mocked."""
    model = new_model(mocked=True)
    assert model.mocked
    assert isinstance(model.model, ModelMocked)
    assert model.model.model_name == "meta-llama/Llama-3.2-3B-Instruct"
    assert model.model.time_to_respond == "short"
    assert model.model.pipe is None
    assert model.model.max_tokens == 8192
    assert model.tokenizer


def test_new_model_actual() -> None:
    """Test the new_model function when mocked is false."""
    model = new_model(mocked=False, model_name="meta-llama/Llama-3.2-3B")
    assert not model.mocked
    assert isinstance(model.model, ModelActual)
    assert model.model.model_name == "meta-llama/Llama-3.2-3B"
    assert isinstance(model.model.pipe, Pipeline)
    assert model.model.max_tokens == 131072
    assert model.tokenizer


def test_token_count(model: Model) -> None:
    """Tests the token count function on a model"""
    chat = [
        ChatMessage(role="user", content="Hi!"),
        ChatMessage(role="assistant", content="Hello!"),
        ChatMessage(role="user", content="How are you?"),
        ChatMessage(role="assistant", content="I'm good."),
    ]
    tokens = model.token_count(chat)
    assert tokens == 16


def test_generate_response(model: Model) -> None:
    """Tests the generate response function on a model"""
    system_message = ChatMessage(role="system", content="You are an assistant.")
    chat = [
        ChatMessage(role="user", content="Hi!"),
        ChatMessage(role="assistant", content="Hello!"),
        ChatMessage(role="user", content="How are you?"),
        ChatMessage(role="assistant", content="I'm good."),
    ]
    response = model.generate_response([system_message] + chat)
    assert response["role"] == "assistant"
    assert response["content"] == "Mock response"
