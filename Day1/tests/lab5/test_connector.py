"""
MA-2041 Lab 5 - connector payload and ACL tests.

These run entirely offline. They never call Microsoft Graph. Lab 5 live
status in this build: NOT EXECUTED.

The ACL tests are the important ones: a connector that over-shares is worse
than a connector that indexes nothing.

Run:  python -m pytest tests/lab5 -q        (from Day1)
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

IMPL = os.environ.get("LAB_IMPL", "solutions")
MODULE_PATH = CODE_ROOT / IMPL / "lab5" / "connector_client.py"


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("lab5_connector_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def articles():
    return json.loads((CODE_ROOT / "fixtures" / "kb_articles.json").read_text(encoding="utf-8"))


def article_by_id(articles, source_id):
    return next(a for a in articles if a["source_id"] == source_id)


# --- connection + schema payloads -----------------------------------------

def test_connection_payload_has_required_fields(mod):
    payload = mod.connection_payload()
    assert payload["id"] == mod.CONNECTION_ID
    assert payload["name"]
    assert payload["description"]


def test_schema_base_type_is_external_item(mod):
    assert mod.schema_payload()["baseType"] == "microsoft.graph.externalItem"


def test_schema_declares_the_properties_items_use(mod, articles):
    declared = {p["name"] for p in mod.schema_payload()["properties"]}
    used = set(mod.transform(articles[0])["properties"])
    missing = used - declared
    assert not missing, "item properties not in the schema: {0}".format(sorted(missing))


def test_schema_labels_title_and_modified(mod):
    labels = {}
    for prop in mod.schema_payload()["properties"]:
        for label in prop.get("labels", []):
            labels[label] = prop["name"]
    assert labels.get("title") == "title"
    assert labels.get("lastModifiedDateTime") == "updated"


# --- ACL: the security tests ----------------------------------------------

def test_acl_never_grants_everyone(mod, articles):
    for article in articles:
        for entry in mod.build_acl(article):
            assert entry["type"] != "everyone"
            assert entry["value"] != "everyone"


def test_acl_matches_the_article_and_is_not_widened(mod, articles):
    article = article_by_id(articles, "KB-102")
    values = {e["value"] for e in mod.build_acl(article)}
    assert values == {"contosohrconfidential"}


def test_acl_entries_are_grants_for_external_groups(mod, articles):
    for entry in mod.build_acl(article_by_id(articles, "KB-101")):
        assert entry["accessType"] == "grant"
        assert entry["type"] == "externalGroup"
        assert set(entry) == {"type", "value", "accessType"}
        assert entry["value"].isascii() and entry["value"].isalnum()


def test_empty_acl_produces_no_grants(mod):
    assert mod.build_acl({"source_id": "KB-999", "acl": []}) == []


def test_item_with_no_acl_is_not_ingested(mod, capsys):
    """An unreachable item beats an over-shared one; ingest must skip it."""
    original = mod.items_to_ingest
    mod.items_to_ingest = lambda: [{"id": "KB999", "properties": {}, "acl": []}]
    try:
        mod.cmd_ingest(live=False)
    finally:
        mod.items_to_ingest = original
    out = capsys.readouterr().out
    assert "refusing to ingest an unreachable item" in out


def test_grant_everyone_helper_refuses(mod):
    with pytest.raises(NotImplementedError):
        mod.grant_everyone()


# --- item shape ------------------------------------------------------------

def test_item_id_has_no_hyphens(mod, articles):
    assert "-" not in mod.transform(articles[0])["id"]


def test_item_datetime_is_iso8601_with_offset(mod, articles):
    updated = mod.transform(article_by_id(articles, "KB-103"))["properties"]["updated"]
    assert "T" in updated
    assert updated.endswith("Z") or "+" in updated


def test_item_version_is_an_int(mod, articles):
    assert isinstance(mod.transform(articles[0])["properties"]["version"], int)


def test_item_content_is_text(mod, articles):
    content = mod.transform(articles[0])["content"]
    assert content["type"] == "text"
    assert content["value"]


# --- safety gates ----------------------------------------------------------

def test_live_is_refused_without_the_env_gate(mod, monkeypatch):
    monkeypatch.delenv(mod.LIVE_GATE_ENV, raising=False)
    with pytest.raises(mod.LiveRefused):
        mod.live_allowed(True)


def test_live_is_refused_without_credentials(mod, monkeypatch):
    monkeypatch.setenv(mod.LIVE_GATE_ENV, "1")
    for key in ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(mod.LiveRefused):
        mod.live_allowed(True)


def test_dry_run_is_the_default(mod):
    assert mod.live_allowed(False) is False


def test_dry_run_sends_nothing(mod, capsys):
    mod.cmd_create_connection(live=False)
    assert "[DRY RUN] not sent" in capsys.readouterr().out
