"""
MA-2041 Lab 5 STARTER - Copilot connector client.

Everything to do with transport, dry-run gating and the CLI is written for
you. You implement the four payload/ACL functions, which are the parts that
decide what gets indexed and who can see it.

DRY RUN IS THE DEFAULT and you should not change that. Run:
    python starters/lab5/connector_client.py plan
Tests:
    $env:LAB_IMPL = "starters"; python -m pytest tests/lab5 -q
"""
from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))
from types import SimpleNamespace
from solutions.lab5 import connector_client as transport
from solutions.lab5.connector_client import (
    CONNECTION_DESCRIPTION, CONNECTION_ID, CONNECTION_NAME, GRAPH_BASE,
    LIVE_GATE_ENV, EXTERNAL_GROUP_IDS, LiveRefused, call, live_allowed,
    poll_operation, grant_everyone, _as_graph_datetime,
)
import json

FIXTURES_DIR = CODE_ROOT / "fixtures"


def connection_payload() -> dict:
    """
    EXERCISE 5.2 (about 12 lines)
    Return the body for POST /external/connections: id, name, description.
    Use CONNECTION_ID / CONNECTION_NAME / CONNECTION_DESCRIPTION.

    Optional: add searchSettings.searchResultTemplates with an Adaptive Card
    layout so results render with a title and an updated date.
    """
    raise NotImplementedError("EXERCISE 5.2: implement connection_payload")


def schema_payload() -> dict:
    """
    EXERCISE 5.3 (about 30 lines)
    Return the body for PATCH /external/connections/{id}/schema.

      * baseType must be "microsoft.graph.externalItem"
      * properties needs at least: title, body, sourceId, owningGroup,
        version (Int64), updated (DateTime)
      * label "title" on the title property and "lastModifiedDateTime" on
        updated, or Copilot renders results badly
      * only set isRefinable on types that support it

    The schema is effectively append-only, so get it right in dry run first.
    """
    raise NotImplementedError("EXERCISE 5.3: implement schema_payload")


def build_acl(article: dict) -> list:
    """
    EXERCISE 5.4 - THE ONE THAT MATTERS (about 10 lines)

    Return the Graph ACL for one article: one entry per group in
    article["acl"], shaped as
        {"type": "externalGroup", "value": EXTERNAL_GROUP_IDS[group],
                 "accessType": "grant"}

    Rules:
      * never widen the article's own ACL
      * an empty ACL produces an empty list - an unreachable item beats an
        over-shared one
      * never emit {"type": "everyone", ...}. tests/lab5 fails the build if
        you do.
    """
    raise NotImplementedError("EXERCISE 5.4: implement build_acl")


def transform(article: dict) -> dict:
    """
    EXERCISE 5.5 (about 15 lines)
    Map one fixture article to a Graph externalItem:
        {"id": ..., "properties": {...}, "content": {...}, "acl": build_acl(article)}

      * id must contain no hyphens (Graph item ids are restricted) - derive it
        from source_id
      * properties keys must match the names you registered in schema_payload
      * version must be an int, updated must be full ISO-8601 with an offset
      * content is {"value": <text>, "type": "text"}
    """
    raise NotImplementedError("EXERCISE 5.5: implement transform")


# Provided transport wrappers bind every command to THIS learner module.
def items_to_ingest():
    return [transform(a) for a in json.loads((FIXTURES_DIR / "kb_articles.json").read_text(encoding="utf-8"))]


def _payloads():
    return SimpleNamespace(connection_payload=connection_payload, schema_payload=schema_payload,
                           items_to_ingest=items_to_ingest)


def cmd_plan(live):
    return transport.cmd_plan(live, _payloads())


def cmd_create_connection(live):
    return transport.cmd_create_connection(live, _payloads())


def cmd_register_schema(live):
    return transport.cmd_register_schema(live, _payloads())


def cmd_ingest(live):
    return transport.cmd_ingest(live, _payloads())


def main(argv=None):
    commands = dict(transport.COMMANDS, plan=cmd_plan,
                    **{"create-connection": cmd_create_connection,
                       "register-schema": cmd_register_schema, "ingest": cmd_ingest})
    return transport.main(argv, commands=commands)


if __name__ == "__main__":
    raise SystemExit(main())
