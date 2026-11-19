"""
MA-2041 Lab 4 STARTER - three separate gates.

A valid signature answers "is this token genuine". It does NOT answer "may
this caller read ticket T-1004". Keep the three functions separate; the tests
check each one independently.

Tests: $env:LAB_IMPL = "starters"; python -m pytest tests/lab4 -q
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import jwt

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.config import settings

FIXTURES_DIR = CODE_ROOT / "fixtures"

FIXTURE_ISSUER = "https://fixture-idp.contoso-helpdesk.test/"
FIXTURE_AUDIENCE = "contoso-helpdesk-api"
REQUIRED_SCOPE = "Tickets.Read"


class AuthnError(Exception):
    """401 - we do not know who you are."""


class AuthzError(Exception):
    """403 - we know who you are and you may not do this."""


def expected_issuer() -> str:
    return settings.get("ENTRA_ISSUER", FIXTURE_ISSUER)


def expected_audience() -> str:
    return settings.get("ENTRA_AUDIENCE", FIXTURE_AUDIENCE)


def signing_key() -> bytes:
    path = FIXTURES_DIR / "fixture_idp_public.pem"
    if not path.exists():
        raise AuthnError("No signing key available to verify tokens.")
    return path.read_bytes()


def bearer_token_from_header(authorization_header):
    """Already written. Returns the raw token or raises AuthnError."""
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthnError("Missing or malformed Authorization header.")
    token = authorization_header[len("Bearer "):].strip()
    if not token:
        raise AuthnError("Empty bearer token.")
    return token


def validate_bearer_token(authorization_header) -> dict:
    """
    EXERCISE 4.3 - GATE 1, authentication (about 15 lines)

    Call bearer_token_from_header(), then jwt.decode() with:
      * signing_key()
      * algorithms=["RS256"]           <- an allow-list of exactly one, so a
                                          token claiming alg=none or HS256
                                          cannot be accepted
      * audience=expected_audience(), issuer=expected_issuer()
      * options requiring exp, iss, aud and sub, with verification ON

    Any jwt.PyJWTError becomes AuthnError. Return the validated claims.

    Negative tests you must pass: forged signature, alg=none, wrong audience,
    wrong issuer, expired. Do NOT use jwt.decode(..., options={"verify_signature": False}).
    """
    raise NotImplementedError("EXERCISE 4.3: implement validate_bearer_token")


def token_scopes(claims: dict) -> set:
    """Already written. Entra puts delegated scopes in `scp`, app roles in `roles`."""
    scopes = {s for s in (claims.get("scp") or "").split() if s}
    roles = claims.get("roles") or []
    if isinstance(roles, list):
        scopes |= set(roles)
    return scopes


def require_scope(claims: dict, scope: str = REQUIRED_SCOPE) -> None:
    """
    EXERCISE 4.4 - GATE 2, scope (about 3 lines)

    Raise AuthzError if `scope` is not in token_scopes(claims). Include the
    scope name in the message - the test greps for "Tickets.Read".

    Note the status code this maps to: a genuine token for the wrong
    permission is 403, not 401.
    """
    raise NotImplementedError("EXERCISE 4.4: implement require_scope")


def caller_groups(claims: dict) -> set:
    """Already written. Groups the VALIDATED token asserts - never a query string."""
    groups = claims.get("groups") or []
    if isinstance(groups, str):
        groups = [g for g in groups.split() if g]
    return set(groups)


def authorize_ticket(claims: dict, ticket: dict) -> None:
    """
    EXERCISE 4.5 - GATE 3, record access (about 10 lines)

    This is the gate the first version of this course was missing.

      * ticket is not restricted            -> allow (return)
      * restricted with no assignee_group   -> raise AuthzError (fail closed)
      * restricted and the caller holds the assignee_group -> allow
      * restricted and the caller does not  -> raise AuthzError

    Include the ticket id and the required group in the message.
    """
    raise NotImplementedError("EXERCISE 4.5: implement authorize_ticket")


def validate_api_key(provided, expected) -> None:
    """
    EXERCISE 4.2 - the API-key gate (about 7 lines)

    Raise AuthnError when:
      * `expected` is falsy      -> a server with no configured key must deny
                                    everything, not allow everything
      * `provided` is missing
      * they do not match

    Use hmac.compare_digest for the comparison, not ==, so the check is
    constant-time.
    """
    raise NotImplementedError("EXERCISE 4.2: implement validate_api_key")
