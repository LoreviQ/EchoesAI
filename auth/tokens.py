import os
from datetime import datetime, timedelta, timezone

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

TOKEN_DURATION = timedelta(days=1)


def _load_private_key() -> RSAPrivateKey:
    with open(".ssh/user-auth", "r", encoding="utf-8") as file:
        private_key = file.read()
    key = serialization.load_ssh_private_key(
        private_key.encode(), password=os.getenv("SSH_KEY_PWD").encode()
    )
    return key


def _load_public_key() -> RSAPublicKey:
    with open(".ssh/user-auth.pub", "r", encoding="utf-8") as file:
        public_key = file.read()
    key = serialization.load_ssh_public_key(public_key.encode())
    return key


def issue_access_token(username: str) -> str:
    """Issues a JWT access token"""
    key = _load_private_key()
    now = datetime.now(timezone.utc)
    payload = {
        "iss": "echoesAI - auth",
        "iat": int(now.timestamp()),
        "exp": int((now + TOKEN_DURATION).timestamp()),
        "sub": username,
    }
    token = jwt.encode(payload, key, algorithm="RS256")
    return token


def auth_access_token(token: str) -> int:
    """Authenticates a JWT access token"""
    public_key = _load_public_key()
    decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
    # Invalid and expired tokens raise errors automatically
    if decoded_token["iss"] != "echoesAI - auth":
        raise ValueError("Invalid token - Wrong issuer")
    return decoded_token["sub"]
