"""
Local FIXTURE IdP for the Lab 4 offline unit tests.

It generates a real RSA keypair and mints real RS256-signed JWTs so the
signature / issuer / audience / expiry / scope / group validation path can be
exercised with no tenant.

THIS IS NOT AN OAUTH FLOW. Keys are generated locally on first test use,
are ignored by Git, and must never be used for real identities.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"
PRIVATE_KEY_PATH = FIXTURES_DIR / "fixture_idp_private.pem"
PUBLIC_KEY_PATH = FIXTURES_DIR / "fixture_idp_public.pem"

ISSUER = "https://fixture-idp.contoso-helpdesk.test/"
AUDIENCE = "contoso-helpdesk-api"
SCOPE = "Tickets.Read"


def ensure_keypair() -> None:
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    PRIVATE_KEY_PATH.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    PUBLIC_KEY_PATH.write_bytes(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _private_key() -> bytes:
    ensure_keypair()
    return PRIVATE_KEY_PATH.read_bytes()


def _mint(payload: dict, key: bytes | None = None) -> str:
    return jwt.encode(payload, key or _private_key(), algorithm="RS256")


def _base(subject: str, expires_in: int = 300) -> dict:
    now = int(time.time())
    return {"sub": subject, "iss": ISSUER, "aud": AUDIENCE, "iat": now, "exp": now + expires_in}


def mint_valid_token(subject: str = "alice.tier1", scope: str = SCOPE, groups=None,
                     expires_in: int = 300) -> str:
    """A genuine token. `groups` defaults to EMPTY - no implicit grants."""
    payload = _base(subject, expires_in)
    payload["scp"] = scope
    payload["groups"] = list(groups or [])
    payload["preferred_username"] = subject
    return _mint(payload)


def mint_token_without_scope(subject: str = "alice.tier1", groups=None) -> str:
    """Structurally valid, correctly signed, but carries no usable scope -> 403."""
    payload = _base(subject)
    payload["scp"] = "User.Read"
    payload["groups"] = list(groups or [])
    return _mint(payload)


def mint_token_for_group(subject: str, group: str) -> str:
    """A genuine token whose holder is a member of one group."""
    return mint_valid_token(subject=subject, groups=[group])


def mint_wrong_audience_token(subject: str = "alice.tier1") -> str:
    payload = _base(subject)
    payload["aud"] = "some-other-api"
    payload["scp"] = SCOPE
    return _mint(payload)


def mint_wrong_issuer_token(subject: str = "alice.tier1") -> str:
    payload = _base(subject)
    payload["iss"] = "https://evil-idp.example.test/"
    payload["scp"] = SCOPE
    return _mint(payload)


def mint_forged_token(subject: str = "attacker", groups=None) -> str:
    """
    Signed with an attacker-controlled key. Structurally a perfect JWT, with
    whatever claims the attacker wants - including group membership. A correct
    implementation rejects it on signature, before ever reading the claims.
    """
    forged = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    payload = _base(subject)
    payload["scp"] = SCOPE
    payload["groups"] = list(groups or ["hr-confidential", "identity-support"])
    return _mint(
        payload,
        forged.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )


def mint_expired_token(subject: str = "alice.tier1") -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now - 1000,
        "exp": now - 500,
        "scp": SCOPE,
        "groups": [],
    }
    return _mint(payload)


def mint_unsigned_token(subject: str = "attacker") -> str:
    """alg=none. Must be rejected by the algorithm allow-list."""
    payload = _base(subject)
    payload["scp"] = SCOPE
    payload["groups"] = ["hr-confidential"]
    return jwt.encode(payload, key="", algorithm="none")
