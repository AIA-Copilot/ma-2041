"""D1_Lab3 reference scaffold: synthetic RS256 signature, issuer, audience, expiry, scope and per-record authorization. Local tests are not an Entra OAuth flow. See ../Labs/D1_Lab3.pdf from the Day1 root."""
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

#: Synthetic fixture IdP parameters for D1_Lab3. Use the local test defaults;
#: this exercise does not require a .env file or a real Entra sign-in.
FIXTURE_ISSUER = "https://fixture-idp.contoso-helpdesk.test/"
FIXTURE_AUDIENCE = "contoso-helpdesk-api"

#: The scope the ticket read operation requires.
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
    """
    Offline: the fixture IdP public key.

    Live: replace this with JWKS retrieval from
    https://login.microsoftonline.com/<tenant>/discovery/v2.0/keys and select
    the key by the token's `kid`. Never disable signature verification.
    """
    path = FIXTURES_DIR / "fixture_idp_public.pem"
    if not path.exists():
        raise AuthnError("No signing key available to verify tokens.")
    return path.read_bytes()


def bearer_token_from_header(authorization_header: str | None) -> str:
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthnError("Missing or malformed Authorization header.")
    token = authorization_header[len("Bearer "):].strip()
    if not token:
        raise AuthnError("Empty bearer token.")
    return token


def validate_bearer_token(authorization_header: str | None) -> dict:
    """
    GATE 1 - authentication. Returns validated claims or raises AuthnError.

    verify_signature is never disabled, and algorithms is an allow-list of one
    so a token with alg=none or alg=HS256 cannot slip through.
    """
    token = bearer_token_from_header(authorization_header)
    try:
        claims = jwt.decode(
            token,
            signing_key(),
            algorithms=["RS256"],
            audience=expected_audience(),
            issuer=expected_issuer(),
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
                "require": ["exp", "iss", "aud", "sub"],
            },
        )
    except jwt.PyJWTError as exc:
        raise AuthnError("Token rejected: {0}".format(type(exc).__name__)) from exc
    return claims


def token_scopes(claims: dict) -> set:
    """Entra ID puts delegated scopes in `scp` (space-delimited) and app roles in `roles`."""
    raw = claims.get("scp") or ""
    scopes = {s for s in raw.split() if s}
    roles = claims.get("roles") or []
    if isinstance(roles, list):
        scopes |= set(roles)
    return scopes


def require_scope(claims: dict, scope: str = REQUIRED_SCOPE) -> None:
    """GATE 2 - scope. A genuine token for a different permission is a 403."""
    if scope not in token_scopes(claims):
        raise AuthzError(
            "Token is valid but lacks the {0} scope. Scopes present: {1}".format(
                scope, sorted(token_scopes(claims)) or "none"
            )
        )


def caller_groups(claims: dict) -> set:
    """
    Groups the validated token asserts. In a real tenant these come from the
    `groups` claim (configure groupMembershipClaims on the app registration)
    or from a Graph lookup - never from a request body or query string.
    """
    groups = claims.get("groups") or []
    if isinstance(groups, str):
        groups = [g for g in groups.split() if g]
    return set(groups)


def authorize_ticket(claims: dict, ticket: dict) -> None:
    """
    GATE 3 - record access.

    An unrestricted ticket is readable by any caller who passed gates 1 and 2.
    A restricted ticket additionally requires the caller to hold the ticket's
    assignee_group. This gate is required independently of authentication.
    """
    if not ticket.get("restricted"):
        return
    required_group = ticket.get("assignee_group")
    if not required_group:
        # Restricted with no owning group: deny. Fail closed.
        raise AuthzError("Ticket is restricted and has no assignee_group; denying.")
    if required_group not in caller_groups(claims):
        raise AuthzError(
            "Ticket {0} is restricted to {1}. Caller holds: {2}".format(
                ticket.get("id"), required_group, sorted(caller_groups(claims)) or "no groups"
            )
        )


def validate_api_key(provided: str | None, expected: str | None) -> None:
    """
    API-key gate for the simpler plugin auth mode.

    Compared with hmac.compare_digest so the comparison is constant-time, and
    a missing configured key denies rather than allowing everything.
    """
    import hmac

    if not expected:
        raise AuthnError("Server has no API key configured; refusing all requests.")
    if not provided:
        raise AuthnError("Missing X-API-Key header.")
    if not hmac.compare_digest(provided, expected):
        raise AuthnError("Invalid API key.")
