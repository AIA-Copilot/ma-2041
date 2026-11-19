"""D1_Lab4 student reference scaffold. Connector schema, payload, ACL and dry-run lifecycle. Run commands from the Day1 root. No Graph writes are authorized by these labs; retain MA2041_ALLOW_LIVE_INGEST=0. See ../Labs/D1_Lab4.pdf."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from common.config import ConfigMissing, settings  # noqa: E402

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
LIVE_GATE_ENV = "MA2041_ALLOW_LIVE_INGEST"

CONNECTION_ID = "contososupportpolicies"
CONNECTION_NAME = "Contoso Support Policies"
CONNECTION_DESCRIPTION = (
    "Contoso published support policies and KB articles, surfaced in Microsoft 365 Copilot."
)

FIXTURES_DIR = CODE_ROOT / "fixtures"

# Stable, reviewed mapping. Unknown groups fail closed (KeyError).
# Before live ingest these external groups and approved members MUST exist.
from types import MappingProxyType
EXTERNAL_GROUP_IDS = MappingProxyType({'collab-support': 'contosocollabsupport', 'desktop-support': 'contosodesktopsupport', 'helpdesk-tier1': 'contosohelpdesktier1', 'helpdesk-tier2': 'contosohelpdesktier2', 'hr-confidential': 'contosohrconfidential', 'identity-support': 'contosoidentitysupport', 'network-support': 'contosonetworksupport', 'public': 'contosopublic', 'security-ops': 'contososecurityops'})


class LiveRefused(RuntimeError):
    """Raised when a live call is attempted without every gate satisfied."""


# ---------------------------------------------------------------------------
# Payload construction - the part students implement and tests check
# ---------------------------------------------------------------------------

def connection_payload() -> dict:
    """
    POST /external/connections

    activitySettings.urlToItemResolvers is omitted on purpose: these items
    have no external web URL, so a resolver would produce dead links.
    """
    return {
        "id": CONNECTION_ID,
        "name": CONNECTION_NAME,
        "description": CONNECTION_DESCRIPTION,
        "searchSettings": {
            "searchResultTemplates": [
                {
                    "id": "contosoSupportPolicy",
                    "priority": 1,
                    "layout": {
                        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.5",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "${title}",
                                "weight": "Bolder",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": "Updated ${updated} | v${version}",
                                "isSubtle": True,
                                "wrap": True,
                            },
                        ],
                    },
                }
            ]
        },
    }


def schema_payload() -> dict:
    """
    PATCH /external/connections/{id}/schema  (long-running, returns 202)

    Property rules that matter and are easy to get wrong:
      * baseType must be "microsoft.graph.externalItem".
      * A property can only be isRefinable/isQueryable/isSearchable if its
        type supports it. Collections cannot be refinable here.
      * labels bind a property to a semantic slot Copilot understands
        (title, url, lastModifiedDateTime...). Without labels the items
        index but render badly.
      * The schema is effectively append-only. Registering a wrong type means
        deleting and recreating the connection - which is why the dry run
        exists.
    """
    return {
        "baseType": "microsoft.graph.externalItem",
        "properties": [
            {
                "name": "title",
                "type": "String",
                "isSearchable": True,
                "isRetrievable": True,
                "isQueryable": True,
                "labels": ["title"],
            },
            {
                "name": "body",
                "type": "String",
                "isSearchable": True,
                "isRetrievable": True,
            },
            {
                "name": "sourceId",
                "type": "String",
                "isRetrievable": True,
                "isQueryable": True,
            },
            {
                "name": "owningGroup",
                "type": "String",
                "isRefinable": True,
                "isRetrievable": True,
                "isQueryable": True,
            },
            {
                "name": "version",
                "type": "Int64",
                "isRetrievable": True,
                "isQueryable": True,
            },
            {
                "name": "updated",
                "type": "DateTime",
                "isRefinable": True,
                "isRetrievable": True,
                "labels": ["lastModifiedDateTime"],
            },
        ],
    }


def transform(article: dict) -> dict:
    """
    Map one fixture KB article to a Graph externalItem.

    `acl` is derived from the article's own ACL - never widened. An article
    with an empty ACL produces an item with NO grants, which is correct:
    unreachable beats over-shared.
    """
    return {
        "id": article["source_id"].replace("-", ""),
        "properties": {
            "title": article["title"],
            "body": article["body"],
            "sourceId": article["source_id"],
            "owningGroup": (article.get("acl") or ["unassigned"])[0],
            "version": int(article.get("version", 1)),
            "updated": _as_graph_datetime(article.get("updated")),
        },
        "content": {"value": article["body"], "type": "text"},
        "acl": build_acl(article),
    }


def _as_graph_datetime(value) -> str:
    """Graph wants full ISO-8601 with an offset; the fixtures hold dates."""
    if not value:
        return "1970-01-01T00:00:00Z"
    value = str(value)
    return value if "T" in value else value + "T00:00:00Z"


def build_acl(article: dict) -> list:
    """
    Build the Graph ACL for one item.

    Each entry grants read to ONE externalGroup, which maps to the Contoso
    group names in fixtures/users.json. The "public" pseudo-group is mapped to
    an explicit Contoso group, not to `everyone`: an item being publicly
    readable inside Contoso is not the same as granting it to everyone in the
    tenant directory, and the connector should not make that decision.
    """
    acl = []
    for group in article.get("acl") or []:
        acl.append(
            {
                "type": "externalGroup",
                "value": EXTERNAL_GROUP_IDS[group],
                "accessType": "grant",
            }
        )
    return acl


def grant_everyone() -> None:
    """
    Deliberately not implemented.

    `{"type": "everyone", "value": "everyone", "accessType": "grant"}` is
    valid Graph and is how connectors accidentally publish restricted content
    to an entire tenant. If you genuinely need a tenant-wide grant, do it
    knowingly in your own code after a data review - not from a training lab.
    """
    raise NotImplementedError(
        "Refusing to build an everyone-grant ACL. Grant specific external groups instead; "
        "see build_acl(). Default deny is the lab's standard."
    )


def items_to_ingest() -> list:
    with open(FIXTURES_DIR / "kb_articles.json", encoding="utf-8") as handle:
        return [transform(a) for a in json.load(handle)]


# ---------------------------------------------------------------------------
# Transport - dry run by default
# ---------------------------------------------------------------------------

def live_allowed(requested: bool) -> bool:
    """All three gates, or no live call."""
    if not requested:
        return False
    if os.environ.get(LIVE_GATE_ENV) != "1":
        raise LiveRefused(
            "--live requires {0}=1 in the environment. Dry run is the default on purpose.".format(
                LIVE_GATE_ENV
            )
        )
    if not settings.graph_configured():
        raise LiveRefused(
            "--live requires GRAPH_TENANT_ID, GRAPH_CLIENT_ID and GRAPH_CLIENT_SECRET in "
            "Day1/.env. Nothing was sent."
        )
    return True


def get_token() -> str:
    """
    Client-credentials token for ExternalConnection.ReadWrite.OwnedBy and ExternalItem.ReadWrite.OwnedBy.

    Called only on the live path. The secret is read through common.config and
    never printed. NOT EXECUTED in this build.
    """
    import requests

    tenant = settings.require("GRAPH_TENANT_ID")
    response = requests.post(
        "https://login.microsoftonline.com/{0}/oauth2/v2.0/token".format(tenant),
        data={
            "client_id": settings.require("GRAPH_CLIENT_ID"),
            "client_secret": settings.require("GRAPH_CLIENT_SECRET"),
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    if response.status_code != 200:
        # Status only. The body can echo client_id and request ids.
        raise RuntimeError(
            "Token request failed with HTTP {0}. Check the app registration and that admin "
            "consent was granted for ExternalConnection.ReadWrite.OwnedBy and ExternalItem.ReadWrite.OwnedBy.".format(response.status_code)
        )
    return response.json()["access_token"]


def call(method: str, url: str, body: dict | None, live: bool, label: str) -> dict | None:
    """Print, then send only if live. Returns the parsed response or None."""
    print("")
    print("--- {0} ---".format(label))
    print("{0} {1}".format(method, url))
    if body is not None:
        print(json.dumps(body, indent=2)[:4000])
    if not live:
        print("[DRY RUN] not sent")
        return None

    import requests

    response = requests.request(
        method,
        url,
        headers={
            "Authorization": "Bearer " + get_token(),
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )
    print("HTTP {0}".format(response.status_code))
    if response.status_code >= 400:
        print("error body: {0}".format(response.text[:1000]))
        response.raise_for_status()
    if response.status_code == 202:
        location = response.headers.get("Location")
        print("async operation: {0}".format(location))
        return {"_operationLocation": location}
    return response.json() if response.content else {}


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_plan(live: bool, payloads=None) -> None:
    items = payloads.items_to_ingest() if payloads is not None else items_to_ingest()
    print("Connection id   : {0}".format(CONNECTION_ID))
    print("Schema properties: {0}".format(
        ", ".join(p["name"] for p in (payloads.schema_payload() if payloads is not None else schema_payload())["properties"])
    ))
    print("Items to ingest : {0}".format(len(items)))
    print("")
    print("{0:<10} {1:<8} {2}".format("item", "grants", "acl values"))
    ungranted = 0
    for item in items:
        values = [a["value"] for a in item["acl"]]
        if not values:
            ungranted += 1
        print("{0:<10} {1:<8} {2}".format(item["id"], len(values), ", ".join(values) or "NONE"))
    print("")
    print("Items with no grants (will be invisible, by design): {0}".format(ungranted))
    print("No 'everyone' grant appears above. If one ever does, that is a bug.")
    print("")
    print("Mode: {0}".format("LIVE" if live else "DRY RUN (default)"))


def cmd_create_connection(live: bool, payloads=None) -> None:
    call("POST", GRAPH_BASE + "/external/connections", (payloads.connection_payload() if payloads is not None else connection_payload()), live,
         "create external connection")


def cmd_register_schema(live: bool, payloads=None) -> None:
    result = call(
        "PATCH",
        "{0}/external/connections/{1}/schema".format(GRAPH_BASE, CONNECTION_ID),
        payloads.schema_payload() if payloads is not None else schema_payload(),
        live,
        "register schema (long-running, expect HTTP 202)",
    )
    if not live:
        print("")
        print("[DRY RUN] Live mode would then poll the Location header until status=succeeded.")
        print("          Schema registration commonly takes 5-15 minutes.")
        return
    location = (result or {}).get("_operationLocation")
    if location:
        poll_operation(location)


def poll_operation(location: str, timeout_seconds: int = 1800, interval: int = 30) -> None:
    """
    Poll a Graph connector async operation to a terminal state.

    Register the schema before ingestion. Without it you ingest against
    a schema that is not ready and every item fails.
    """
    import requests

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = requests.get(
            location, headers={"Authorization": "Bearer " + get_token()}, timeout=30
        )
        payload = response.json()
        status = payload.get("status")
        print("operation status: {0}".format(status))
        if status == "succeeded":
            return
        if status == "failed":
            raise RuntimeError("Schema registration failed: {0}".format(payload.get("error")))
        time.sleep(interval)
    raise TimeoutError("Schema registration did not finish within {0}s.".format(timeout_seconds))


def cmd_ingest(live: bool, payloads=None) -> None:
    items = payloads.items_to_ingest() if payloads is not None else items_to_ingest()
    print("Ingesting {0} items into {1}".format(len(items), CONNECTION_ID))
    for item in items:
        if not item["acl"]:
            print("skipping {0}: no ACL grants, refusing to ingest an unreachable item".format(
                item["id"]
            ))
            continue
        call(
            "PUT",
            "{0}/external/connections/{1}/items/{2}".format(GRAPH_BASE, CONNECTION_ID, item["id"]),
            item,
            live,
            "upsert item {0}".format(item["id"]),
        )


def cmd_status(live: bool) -> None:
    call("GET", "{0}/external/connections/{1}".format(GRAPH_BASE, CONNECTION_ID), None, live,
         "connection state")
    call("GET", "{0}/external/connections/{1}/schema".format(GRAPH_BASE, CONNECTION_ID), None,
         live, "registered schema")
    print("")
    print("Also check, in the browser:")
    print("  Microsoft 365 admin center > Settings > Search & intelligence > Data sources")
    print("  - connection state should be 'Ready'")
    print("  - the Connections tab shows item counts and per-item ingestion errors")


def cmd_troubleshoot(live: bool) -> None:
    print("Lab 5 troubleshooting checklist")
    print("")
    rows = [
        ("HTTP 401 on token request",
         "Admin consent not granted. Entra ID > App registrations > your app > API permissions > "
         "Grant admin consent for ExternalConnection.ReadWrite.OwnedBy and ExternalItem.ReadWrite.OwnedBy."),
        ("HTTP 403 on connection create",
         "Token has the permission but as a delegated scope. Connector writes need the "
         "APPLICATION permission and client-credentials flow."),
        ("HTTP 409 on connection create",
         "The connection id already exists. GET it, or DELETE and recreate - ids are not "
         "reusable while a connection is active."),
        ("Schema 202 then status=failed",
         "Almost always an illegal property flag combination. Re-read schema_payload(); "
         "isRefinable is not valid on every type."),
        ("Items ingest but never appear in Copilot",
         "Three usual causes: the schema operation never reached succeeded; the item ACLs "
         "grant groups that do not exist; or the declarative agent's "
         "CopilotConnectors connectionId does not match CONNECTION_ID."),
        ("Items appear for the wrong people",
         "Stop and audit build_acl(). Then delete the affected items. This is the failure "
         "mode that matters - over-sharing is worse than not indexing."),
        ("Everything 'works' but results are stale",
         "Re-ingest. This client upserts by item id, so re-running ingest is safe and "
         "idempotent."),
    ]
    for symptom, fix in rows:
        print("  * {0}".format(symptom))
        print("      {0}".format(fix))
    print("")
    print("Verify the connection id the agent uses:")
    print("  solutions/lab1/main.tsp -> AgentCapabilities.CopilotConnectors connectionId")
    print("  must equal '{0}'".format(CONNECTION_ID))


COMMANDS = {
    "plan": cmd_plan,
    "create-connection": cmd_create_connection,
    "register-schema": cmd_register_schema,
    "ingest": cmd_ingest,
    "status": cmd_status,
    "troubleshoot": cmd_troubleshoot,
}


def main(argv=None, commands=None) -> int:
    parser = argparse.ArgumentParser(description="MA-2041 Lab 5 Copilot connector client")
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually call Microsoft Graph. Also requires {0}=1 and full credentials.".format(
            LIVE_GATE_ENV
        ),
    )
    args = parser.parse_args(argv)

    try:
        live = live_allowed(args.live)
    except (LiveRefused, ConfigMissing) as exc:
        print("LIVE REFUSED: {0}".format(exc))
        return 2

    if live:
        print("*** LIVE MODE - this will write to the tenant. ***")

    (commands if commands is not None else COMMANDS)[args.command](live)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
