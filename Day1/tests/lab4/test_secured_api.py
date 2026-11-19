"""Local synthetic-token tests for D1_Lab3: verify authentication and per-record authorization separately. Run python -m pytest tests/lab4 -q from Day1; choose LAB_IMPL explicitly."""
from __future__ import annotations

import importlib.util
import os
import secrets
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixture_idp import (  # noqa: E402
    mint_expired_token,
    mint_forged_token,
    mint_token_for_group,
    mint_token_without_scope,
    mint_unsigned_token,
    mint_valid_token,
    mint_wrong_audience_token,
    mint_wrong_issuer_token,
)

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
IMPL = os.environ.get("LAB_IMPL", "solutions")
APP_PATH = CODE_ROOT / IMPL / "lab4" / "app.py"
TEST_API_KEY = secrets.token_hex(16)


def load_app_module():
    os.environ["LAB4_API_KEY"] = TEST_API_KEY
    spec = importlib.util.spec_from_file_location("lab4_app_under_test", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def client():
    module = load_app_module()
    module.app.testing = True
    return module.app.test_client()


def bearer(token: str) -> dict:
    return {"Authorization": "Bearer " + token}


# ---------------------------------------------------------------------------
# API key gate
# ---------------------------------------------------------------------------

def test_apikey_correct_key_allowed(client):
    response = client.get("/secure/apikey/tickets/T-1001", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    assert response.get_json()["id"] == "T-1001"


def test_apikey_missing_key_denied(client):
    assert client.get("/secure/apikey/tickets/T-1001").status_code == 401


def test_apikey_wrong_key_denied(client):
    response = client.get(
        "/secure/apikey/tickets/T-1001", headers={"X-API-Key": "not-the-key"}
    )
    assert response.status_code == 401


def test_apikey_cannot_read_restricted_ticket(client):
    """
    An API key is an APPLICATION identity with no user groups. T-1004 is
    restricted to hr-confidential, so the correct answer is 403 - not the
    record.
    """
    response = client.get("/secure/apikey/tickets/T-1004", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 403
    assert "hr-confidential" in response.get_json()["detail"]


def test_apikey_response_does_not_leak_restricted_body(client):
    response = client.get("/secure/apikey/tickets/T-1004", headers={"X-API-Key": TEST_API_KEY})
    assert "salaries" not in response.get_data(as_text=True)


# ---------------------------------------------------------------------------
# Gate 1 - authentication
# ---------------------------------------------------------------------------

def test_oauth_valid_token_allowed(client):
    response = client.get("/secure/oauth/tickets/T-1001", headers=bearer(mint_valid_token()))
    assert response.status_code == 200
    assert response.get_json()["id"] == "T-1001"


def test_oauth_missing_token_denied(client):
    assert client.get("/secure/oauth/tickets/T-1001").status_code == 401


def test_oauth_malformed_header_denied(client):
    response = client.get(
        "/secure/oauth/tickets/T-1001", headers={"Authorization": "Basic abc123"}
    )
    assert response.status_code == 401


def test_oauth_forged_signature_denied(client):
    """
    The forged token asserts hr-confidential membership. It must be rejected
    on signature, so the claims are never even consulted.
    """
    response = client.get("/secure/oauth/tickets/T-1004", headers=bearer(mint_forged_token()))
    assert response.status_code == 401


def test_oauth_unsigned_alg_none_denied(client):
    response = client.get("/secure/oauth/tickets/T-1004", headers=bearer(mint_unsigned_token()))
    assert response.status_code == 401


def test_oauth_wrong_audience_denied(client):
    response = client.get(
        "/secure/oauth/tickets/T-1001", headers=bearer(mint_wrong_audience_token())
    )
    assert response.status_code == 401


def test_oauth_wrong_issuer_denied(client):
    response = client.get(
        "/secure/oauth/tickets/T-1001", headers=bearer(mint_wrong_issuer_token())
    )
    assert response.status_code == 401


def test_oauth_expired_token_denied(client):
    response = client.get("/secure/oauth/tickets/T-1001", headers=bearer(mint_expired_token()))
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Gate 2 - scope
# ---------------------------------------------------------------------------

def test_valid_token_without_required_scope_is_forbidden(client):
    """Genuine token, wrong permission. 403, not 401, and not 200."""
    response = client.get(
        "/secure/oauth/tickets/T-1001", headers=bearer(mint_token_without_scope())
    )
    assert response.status_code == 403
    assert "Tickets.Read" in response.get_json()["detail"]


# ---------------------------------------------------------------------------
# Gate 3 - record access. AUTHENTICATION IS NOT AUTHORIZATION.
# ---------------------------------------------------------------------------

def test_valid_token_cannot_read_restricted_ticket_without_group(client):
    """
    THE regression test for this lab. alice.tier1 is fully authenticated and
    has the right scope, and must still be refused T-1004.
    """
    response = client.get("/secure/oauth/tickets/T-1004", headers=bearer(mint_valid_token()))
    assert response.status_code == 403
    body = response.get_data(as_text=True)
    assert "salaries" not in body


def test_token_with_correct_group_can_read_restricted_ticket(client):
    token = mint_token_for_group("dave.hr", "hr-confidential")
    response = client.get("/secure/oauth/tickets/T-1004", headers=bearer(token))
    assert response.status_code == 200
    assert response.get_json()["id"] == "T-1004"


def test_group_membership_does_not_cross_records(client):
    """Holding hr-confidential must not unlock the identity-support ticket."""
    token = mint_token_for_group("dave.hr", "hr-confidential")
    response = client.get("/secure/oauth/tickets/T-1002", headers=bearer(token))
    assert response.status_code == 403


def test_listing_hides_unreadable_restricted_tickets(client):
    response = client.get("/secure/oauth/tickets", headers=bearer(mint_valid_token()))
    assert response.status_code == 200
    ids = [t["id"] for t in response.get_json()["value"]]
    assert "T-1004" not in ids
    assert "T-1002" not in ids
    assert "T-1001" in ids


def test_listing_includes_restricted_ticket_for_authorized_group(client):
    token = mint_token_for_group("dave.hr", "hr-confidential")
    response = client.get("/secure/oauth/tickets", headers=bearer(token))
    ids = [t["id"] for t in response.get_json()["value"]]
    assert "T-1004" in ids
    assert "T-1002" not in ids


def test_unknown_ticket_is_404_after_auth(client):
    response = client.get("/secure/oauth/tickets/T-9999", headers=bearer(mint_valid_token()))
    assert response.status_code == 404


def test_server_without_api_key_fails_closed(monkeypatch):
    """No configured key must deny everything, not allow everything."""
    monkeypatch.delenv("LAB4_API_KEY", raising=False)
    spec = importlib.util.spec_from_file_location("lab4_app_nokey", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.API_KEY = None
    module.app.testing = True
    client_nokey = module.app.test_client()
    response = client_nokey.get(
        "/secure/apikey/tickets/T-1001", headers={"X-API-Key": "anything"}
    )
    assert response.status_code == 401
