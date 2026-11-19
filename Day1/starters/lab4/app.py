"""
MA-2041 Lab 4 - PROVIDED ROUTE SCAFFOLD - the Contoso ticket API with two plugin auth modes.

  /secure/apikey/tickets/<id>   X-API-Key header (plugin auth: apiKeyPluginVault)
  /secure/oauth/tickets/<id>    Bearer JWT      (plugin auth: oAuthPluginVault)

Both routes run the three gates in starters/lab4/token_validation.py:
authenticate, then check scope, then check record access. A valid signature
alone gets you nothing.

Status codes are meaningful:
  401  we could not establish who you are
  403  we know who you are and you may not read this record
  404  no such ticket

Run:   python solutions/lab4/app.py          (binds 127.0.0.1:5001 only)
Tests: python -m pytest tests/lab4 -q        (from Day1)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, request

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from token_validation import (  # noqa: E402
    REQUIRED_SCOPE,
    AuthnError,
    AuthzError,
    authorize_ticket,
    require_scope,
    validate_api_key,
    validate_bearer_token,
)

app = Flask(__name__)
FIXTURES_DIR = CODE_ROOT / "fixtures"

#: Generated at runtime, never checked in. The lab generates one with
#: `python -c "import secrets; print(secrets.token_hex(16))"` and exports it.
from common.config import settings
API_KEY = settings.get("LAB4_API_KEY")

#: Groups an API-key caller is treated as holding. Deliberately EMPTY: an API
#: key identifies an application, not a person, so it must not inherit any
#: user's group membership. Restricted tickets are therefore unreachable with
#: an API key - that is the correct answer, not a limitation to work around.
API_KEY_GROUPS: list = []


def load_tickets() -> list:
    with open(FIXTURES_DIR / "tickets.json", encoding="utf-8") as handle:
        return json.load(handle)


def find_ticket(ticket_id: str):
    return next((t for t in load_tickets() if t["id"] == ticket_id), None)


def public_view(ticket: dict) -> dict:
    """Never return the whole record; project only the fields the plugin needs."""
    return {
        "id": ticket["id"],
        "title": ticket["title"],
        "body": ticket["body"],
        "status": ticket["status"],
        "assignee_group": ticket["assignee_group"],
    }


@app.get("/secure/apikey/tickets")
def list_tickets_apikey():
    try:
        validate_api_key(request.headers.get("X-API-Key"), API_KEY)
    except AuthnError as exc:
        return jsonify({"error": "unauthorized", "detail": str(exc)}), 401
    # Application credentials confer no human group membership.
    visible = [public_view(t) for t in load_tickets() if not t.get("restricted")]
    return jsonify({"value": visible, "count": len(visible)})


@app.get("/secure/apikey/tickets/<ticket_id>")
def get_ticket_apikey(ticket_id: str):
    try:
        validate_api_key(request.headers.get("X-API-Key"), API_KEY)
    except AuthnError as exc:
        return jsonify({"error": "unauthorized", "detail": str(exc)}), 401

    ticket = find_ticket(ticket_id)
    if ticket is None:
        return jsonify({"error": "not_found"}), 404

    # An API key is an application identity with no user groups, so a
    # restricted ticket is a 403 - not a silent full-record disclosure.
    claims = {"sub": "apikey-client", "scp": REQUIRED_SCOPE, "groups": API_KEY_GROUPS}
    try:
        authorize_ticket(claims, ticket)
    except AuthzError as exc:
        return jsonify({"error": "forbidden", "detail": str(exc)}), 403

    return jsonify(public_view(ticket))


@app.get("/secure/oauth/tickets/<ticket_id>")
def get_ticket_oauth(ticket_id: str):
    try:
        claims = validate_bearer_token(request.headers.get("Authorization"))
    except AuthnError as exc:
        return jsonify({"error": "unauthorized", "detail": str(exc)}), 401

    try:
        require_scope(claims, REQUIRED_SCOPE)
    except AuthzError as exc:
        return jsonify({"error": "forbidden", "detail": str(exc)}), 403

    ticket = find_ticket(ticket_id)
    if ticket is None:
        return jsonify({"error": "not_found"}), 404

    try:
        authorize_ticket(claims, ticket)
    except AuthzError as exc:
        return jsonify({"error": "forbidden", "detail": str(exc)}), 403

    return jsonify(public_view(ticket))


@app.get("/secure/oauth/tickets")
def list_tickets_oauth():
    """
    Listing applies the SAME record-level gate per item, so a caller never
    sees a restricted ticket's existence in a list it could not read directly.
    """
    try:
        claims = validate_bearer_token(request.headers.get("Authorization"))
        require_scope(claims, REQUIRED_SCOPE)
    except AuthnError as exc:
        return jsonify({"error": "unauthorized", "detail": str(exc)}), 401
    except AuthzError as exc:
        return jsonify({"error": "forbidden", "detail": str(exc)}), 403

    visible = []
    for ticket in load_tickets():
        try:
            authorize_ticket(claims, ticket)
        except AuthzError:
            continue
        visible.append(public_view(ticket))
    return jsonify({"value": visible, "count": len(visible)})


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "api_key_configured": bool(API_KEY)})


if __name__ == "__main__":
    if not API_KEY:
        print(
            "LAB4_API_KEY is not set. The API-key route will refuse every request "
            "(fail closed). Generate one:\n"
            '  $env:LAB4_API_KEY = python -c "import secrets; print(secrets.token_hex(16))"'
        )
    app.run(host="127.0.0.1", port=5001, debug=False)
