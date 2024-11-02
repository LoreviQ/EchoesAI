"""This file contains the tests for the chatbot/response.py file."""

# pylint: disable=redefined-outer-name unused-argument unused-import

import importlib
from datetime import datetime, timedelta, timezone

import database as db
from chatbot import Model, new_model, response_cycle
from tests.test_chatbot.test_model import model

types_module = importlib.import_module("chatbot.types")
ChatMessage = getattr(types_module, "ChatMessage")
response_module = importlib.import_module("chatbot.response")
Messages = getattr(response_module, "Messages")
_get_response_time = getattr(response_module, "_get_response_time")
_get_response_and_submit = getattr(response_module, "_get_response_and_submit")


# TODO
