"""D1_Lab2 learner API scaffold. Follow ../Labs/D1_Lab2.pdf from the Day1 root. Keep fixture services on loopback."""
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
    """Projection helper - already written for you. Note `restricted` is absent."""
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
    """
    EXERCISE 2.3 (about 6 lines)
    Find the ticket whose "id" equals ticket_id in load_tickets().
      * not found  -> abort(404)
      * found      -> return jsonify(public_view(ticket))
    Do not return the raw fixture dict: it carries a `restricted` flag that
    must not go on the wire.
    """
    raise NotImplementedError("EXERCISE 2.3: implement get_ticket")


@app.get("/tickets")
def list_tickets():
    """
    EXERCISE 2.5 (about 8 lines)
    Return {"value": [...], "count": n} for the tickets a caller with NO
    identity may see.

    Decide and defend: this route has no authentication, so there is nobody to
    authorize. Which tickets belong in the response? Look at the `restricted`
    flag in fixtures/tickets.json before you answer, and support ?status=open.

    The negative test in tests/lab2_3 asserts that T-1004 never appears here.
    """
    raise NotImplementedError("EXERCISE 2.5: implement list_tickets")


def build_adaptive_card(ticket: dict) -> dict:
    """
    EXERCISE 3.2 (about 20 lines)
    Return a valid Adaptive Card 1.5 dict showing at least the ticket id,
    title, status and assignee_group.

    Required: "$schema", "type": "AdaptiveCard", "version": "1.5", and a
    "body" list. Use a TextBlock for the heading and a FactSet for status and
    owning group. tests/lab2_3 validates this against the real Adaptive Cards
    JSON schema in fixtures/adaptive_card_schema.json, so a near-miss fails.

    Then compare your card against the `static_template` block in
    appPackage/ai-plugin.json and note the difference: the manifest version
    uses ${id} style placeholders because Copilot binds it to the HTTP
    response, while this function already has the values.
    """
    raise NotImplementedError("EXERCISE 3.2: implement build_adaptive_card")


@app.get("/tickets/<ticket_id>/card")
def get_ticket_card(ticket_id: str):
    ticket = next((t for t in load_tickets() if t["id"] == ticket_id), None)
    if ticket is None:
        abort(404)
    return jsonify(build_adaptive_card(ticket))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
