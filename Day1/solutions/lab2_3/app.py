"""
MA-2041 Labs 2+3 - SOLUTION - the Contoso ticket API behind the Copilot plugin.

Lab 2 surfaces the API: GET /tickets/<id> and GET /tickets are the two
operations the API plugin calls (see appPackage/openapi.json).
Lab 3 adds the Adaptive Card: build_adaptive_card() renders a ticket, and the
same card shape is embedded as `static_template` in appPackage/ai-plugin.json
so Copilot can render results without calling the card endpoint at all.

Run:   python solutions/lab2_3/app.py        (binds 127.0.0.1:5000 only)
Tests: python -m pytest tests/lab2_3 -q     (from Day1)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from flask import Flask, abort, jsonify, request

CODE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

app = Flask(__name__)
FIXTURES_DIR = CODE_ROOT / "fixtures"


def load_tickets() -> list:
    with open(FIXTURES_DIR / "tickets.json", encoding="utf-8") as handle:
        return json.load(handle)


def public_view(ticket: dict) -> dict:
    """Project only what the plugin needs. `restricted` never goes on the wire."""
    return {
        "id": ticket["id"],
        "title": ticket["title"],
        "body": ticket["body"],
        "status": ticket["status"],
        "assignee_group": ticket["assignee_group"],
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/tickets/<ticket_id>")
def get_ticket(ticket_id: str):
    ticket = next((t for t in load_tickets() if t["id"] == ticket_id), None)
    if ticket is None:
        abort(404)
    return jsonify(public_view(ticket))


@app.get("/tickets")
def list_tickets():
    """
    This unauthenticated route deliberately omits restricted tickets. Labs 2/3
    have no caller identity, so there is nobody to authorize - the safe answer
    is to publish only the non-restricted records. Lab 4 adds identity and
    re-admits restricted records to the callers entitled to them.
    """
    status = request.args.get("status")
    tickets = [t for t in load_tickets() if not t.get("restricted")]
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    return jsonify({"value": [public_view(t) for t in tickets], "count": len(tickets)})


def build_adaptive_card(ticket: dict) -> dict:
    """
    Adaptive Card 1.5 for one ticket.

    Keep this in step with the `static_template` in appPackage/ai-plugin.json.
    The manifest version uses ${placeholders} because Copilot binds it to the
    response; this version substitutes real values for the local /card route.
    """
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": "{0} - {1}".format(ticket["id"], ticket["title"]),
                "weight": "Bolder",
                "size": "Medium",
                "wrap": True,
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Status", "value": ticket["status"]},
                    {"title": "Owning group", "value": ticket["assignee_group"]},
                ],
            },
            {"type": "TextBlock", "text": ticket["body"], "wrap": True, "isSubtle": True},
        ],
    }


@app.get("/tickets/<ticket_id>/card")
def get_ticket_card(ticket_id: str):
    ticket = next((t for t in load_tickets() if t["id"] == ticket_id), None)
    if ticket is None:
        abort(404)
    return jsonify(build_adaptive_card(ticket))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
