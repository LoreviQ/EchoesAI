"""
This file contains the tests for the auth/passwords.py file.
"""

import time
from datetime import timedelta
from typing import Generator

import dotenv
import jwt
import pytest

import auth

# pylint: disable=redefined-outer-name unused-argument unused-import


@pytest.fixture
def user() -> Generator[None, None, None]:
    """
    sets environment variables for testing.
    """
    dotenv.load_dotenv()
    yield None


def test_issue_access_token():
    """
    Test the issue_access_token function.
    """
    token = auth.issue_access_token(1)
    assert isinstance(token, str)


def test_auth_access_token():
    """
    Test the auth_access_token function.
    """
    token = auth.issue_access_token(1)
    user_id = auth.auth_access_token(token)
    assert user_id == "1"
    with pytest.raises(jwt.InvalidTokenError):
        auth.auth_access_token("invalid_token")


def test_auth_access_token_expired(monkeypatch: pytest.MonkeyPatch):
    """
    Test that the auth_access_token function raises an error when the token is expired.
    """
    duration = timedelta(seconds=1)
    monkeypatch.setattr("auth.tokens.TOKEN_DURATION", duration)
    token = auth.issue_access_token(1)
    time.sleep(2)
    with pytest.raises(jwt.ExpiredSignatureError):
        auth.auth_access_token(token)
