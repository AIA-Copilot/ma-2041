"""
D1_Lab2 local API and card tests. LAB_IMPL defaults to solutions;
set it explicitly to starters when testing learner edits.
"""
import importlib.util
import json
import os
import sys
import urllib.request

import pytest

HERE = os.path.dirname(__file__)
IMPL = os.environ.get("LAB_IMPL", "solutions")
APP_PATH = os.path.join(HERE, "..", "..", IMPL, "lab2_3", "app.py")


def load_app_module():
    spec = importlib.util.spec_from_file_location("lab2_3_app", APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def client():
    mod = load_app_module()
    mod.app.testing = True
    return mod.app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_get_known_ticket(client):
    r = client.get("/tickets/T-1001")
    assert r.status_code == 200
    body = r.get_json()
    assert body["id"] == "T-1001"
    assert "VPN" in body["title"]


def test_get_unknown_ticket_404(client):
    r = client.get("/tickets/T-9999")
    assert r.status_code == 404


SCHEMA_CACHE = os.path.join(HERE, "..", "..", "fixtures", "adaptive_card_schema.json")


def get_adaptive_card_schema():
    """Fetch and cache the official Adaptive Cards JSON schema; fall back to a minimal local shape check if offline."""
    if os.path.exists(SCHEMA_CACHE):
        with open(SCHEMA_CACHE, encoding="utf-8") as f:
            return json.load(f)
    try:
        url = "https://adaptivecards.io/schemas/adaptive-card.json"
        with urllib.request.urlopen(url, timeout=5) as resp:
            schema = json.loads(resp.read())
        with open(SCHEMA_CACHE, "w", encoding="utf-8") as f:
            json.dump(schema, f)
        return schema
    except Exception:
        return None


def test_adaptive_card_shape(client):
    r = client.get("/tickets/T-1001/card")
    assert r.status_code == 200
    card = r.get_json()
    assert card["type"] == "AdaptiveCard"
    assert card["version"] == "1.5"
    assert isinstance(card["body"], list) and len(card["body"]) > 0

    schema = get_adaptive_card_schema()
    if schema is None:
        pytest.skip("Official Adaptive Cards schema unreachable (offline) - shape-only assertions above still ran")
    import jsonschema
    jsonschema.Draft7Validator(schema).validate(card)


def test_card_for_unknown_ticket_404(client):
    r = client.get("/tickets/T-9999/card")
    assert r.status_code == 404
