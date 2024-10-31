"""
This file contains the tests for the auth/passwords.py file.
"""

# pylint: disable=redefined-outer-name unused-argument unused-import

import time
from datetime import timedelta

import jwt
import pytest

import auth


def test_issue_access_token() -> None:
    """
    Test the issue_access_token function.
    """
    token = auth.issue_access_token("user")
    assert isinstance(token, str)


def test_auth_access_token() -> None:
    """
    Test the auth_access_token function.
    """
    token = auth.issue_access_token("user")
    user = auth.auth_access_token(token)
    assert user == "user"
    with pytest.raises(jwt.InvalidTokenError):
        auth.auth_access_token("invalid_token")


def test_auth_access_token_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the auth_access_token function raises an error when the token is expired.
    """
    duration = timedelta(seconds=1)
    monkeypatch.setattr("auth.tokens.TOKEN_DURATION", duration)
    token = auth.issue_access_token("user")
    time.sleep(2)
    with pytest.raises(jwt.ExpiredSignatureError):
        auth.auth_access_token(token)
