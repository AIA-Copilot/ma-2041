"""Synthetic classroom identities and default-deny record authorization. Never treat chat text or a channel application identity as a human identity."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

#: The only group an unauthenticated caller ever holds.
PUBLIC_GROUP = "public"

#: Env var selecting how the host is allowed to resolve identity.
IDENTITY_MODE_ENV = "MA2041_IDENTITY_MODE"

#: Loopback-only guard. FIXTURE_LOCAL is refused unless the host sets this to
#: "1". Local tests set it; a tunnelled or deployed host must not.
LOOPBACK_ONLY_ENV = "MA2041_LOOPBACK_ONLY"

#: Reserved channel_data key for the simulated-principal injection point.
#: Named loudly so it is obvious in any trace that this is a test injection
#: and not a real identity.
INJECTED_PRINCIPAL_KEY = "ma2041SimulatedTestPrincipal"


class IdentitySource(str, Enum):
    ANONYMOUS = "anonymous"
    FIXTURE_LOCAL = "fixture-local-simulated"
    VERIFIED_CHANNEL = "verified-channel"


class IdentityMode(str, Enum):
    #: Default. No identity is ever accepted; public knowledge only.
    ANONYMOUS = "anonymous"
    #: Local teaching mode. Simulated principals accepted, loopback only.
    FIXTURE_LOCAL = "fixture-local"
    #: Unsupported user SSO: channel mode fails closed to anonymous.
    CHANNEL = "channel"


class IdentityRefused(PermissionError):
    """Raised when a caller asserts an identity it is not allowed to assert."""


@dataclass(frozen=True)
class Principal:
    """
    An identity the agent is willing to make authorization decisions about.

    `authenticated` is True only for FIXTURE_LOCAL (explicitly simulated and
    labelled as such). VERIFIED_CHANNEL is reserved and never emitted. It is never True because a user
    typed something into the chat.
    """

    id: str
    groups: frozenset
    source: IdentitySource
    authenticated: bool

    @property
    def is_simulated(self) -> bool:
        return self.source is IdentitySource.FIXTURE_LOCAL

    def label(self) -> str:
        if self.source is IdentitySource.ANONYMOUS:
            return "anonymous (public knowledge only)"
        if self.source is IdentitySource.FIXTURE_LOCAL:
            return self.id + " [SIMULATED local test principal - NOT authenticated]"
        return self.id + " [verified channel identity]"


#: The principal used whenever nothing authenticated the caller.
ANONYMOUS = Principal(
    id="anonymous",
    groups=frozenset({PUBLIC_GROUP}),
    source=IdentitySource.ANONYMOUS,
    authenticated=False,
)


def load_users() -> list:
    with open(FIXTURES_DIR / "users.json", encoding="utf-8") as handle:
        return json.load(handle)


def _groups_for(username: str) -> Optional[frozenset]:
    for user in load_users():
        if user["username"] == username:
            # Every authenticated principal also holds the public group, so
            # public articles stay visible to signed-in users too.
            return frozenset(set(user["groups"]) | {PUBLIC_GROUP})
    return None


def current_mode() -> IdentityMode:
    raw = (os.environ.get(IDENTITY_MODE_ENV) or IdentityMode.ANONYMOUS.value).strip().lower()
    try:
        return IdentityMode(raw)
    except ValueError:
        # An unrecognised mode fails CLOSED, not open.
        return IdentityMode.ANONYMOUS


def make_fixture_principal(username: str, allow_non_loopback: bool = False) -> Principal:
    """
    Build a SIMULATED principal for local teaching and for tests.

    Refuses unless the host declared loopback-only operation. This flag is
    NOT a network control: never expose fixture mode through a tunnel.
    """
    if current_mode() is not IdentityMode.FIXTURE_LOCAL:
        raise IdentityRefused(
            "Simulated principals require {0}=fixture-local. Current mode: {1}.".format(
                IDENTITY_MODE_ENV, current_mode().value
            )
        )
    if not allow_non_loopback and os.environ.get(LOOPBACK_ONLY_ENV) != "1":
        raise IdentityRefused(
            "Simulated principals require {0}=1 (loopback-only host). Never enable "
            "fixture-local mode on a tunnelled or deployed host.".format(LOOPBACK_ONLY_ENV)
        )
    groups = _groups_for(username)
    if groups is None:
        raise IdentityRefused(
            "Unknown principal {0!r}. Unknown principals get no access.".format(username)
        )
    return Principal(
        id=username,
        groups=groups,
        source=IdentitySource.FIXTURE_LOCAL,
        authenticated=True,
    )


def principal_from_verified_claims(claims: dict) -> Principal:
    """Channel caller claims are NOT a human SSO token.

    User-token/SSO validation and tenant/object-ID mapping are unsupported
    live gates. Never map channel subjects to the local fixture roster.
    """
    return ANONYMOUS


def _injected_principal_id(turn_context) -> Optional[str]:
    activity = getattr(turn_context, "activity", None)
    channel_data = getattr(activity, "channel_data", None) or {}
    if isinstance(channel_data, dict):
        value = channel_data.get(INJECTED_PRINCIPAL_KEY)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _verified_claims(turn_context) -> Optional[dict]:
    """
    In CHANNEL mode the hosting layer attaches validated claims to the turn.
    The SDK channel authentication middleware is what validates the inbound
    JWT; we only read its result. We never validate a token here.
    """
    identity = getattr(turn_context, "identity", None)
    claims = getattr(identity, "claims", None)
    if isinstance(claims, dict) and claims:
        return claims
    return None


def resolve_principal(turn_context=None) -> Principal:
    """
    The ONLY function an agent handler should call to learn who it is talking
    to. It deliberately never reads turn_context.activity.text.
    """
    mode = current_mode()

    if mode is IdentityMode.ANONYMOUS:
        return ANONYMOUS

    if mode is IdentityMode.FIXTURE_LOCAL:
        # The local test fixture injects the
        # simulated principal into channel_data under the reserved key. Chat
        # text is not consulted. If the host injected nothing, stay anonymous.
        injected = _injected_principal_id(turn_context)
        if not injected:
            return ANONYMOUS
        try:
            return make_fixture_principal(injected)
        except IdentityRefused:
            return ANONYMOUS

    # Channel caller validation does not authenticate a human.
    claims = _verified_claims(turn_context)
    if not claims:
        return ANONYMOUS
    try:
        return principal_from_verified_claims(claims)
    except IdentityRefused:
        return ANONYMOUS


# ---------------------------------------------------------------------------
# Authorization - a separate decision from authentication.
# ---------------------------------------------------------------------------

def authorize_article(principal: Principal, article: dict) -> bool:
    """
    Decide whether `principal` may see one KB article.

    Rules, in order:
      1. Public articles are visible to everyone, including anonymous.
      2. Anything else requires an authenticated principal.
      3. An authenticated principal still needs a group that appears in the
         article ACL. Authentication alone grants nothing.
    """
    acl = set(article.get("acl") or [])
    if PUBLIC_GROUP in acl:
        return True
    if not principal.authenticated:
        return False
    return bool(acl & set(principal.groups))


def visible_articles(principal: Principal, articles: Iterable) -> list:
    return [a for a in articles if authorize_article(principal, a)]
