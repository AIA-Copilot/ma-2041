"""Offline regression against exact upstream Toolkit metadata, not a local enum."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
METADATA_SHA256 = "6e0e360f0e5b0252c6e4c4a30b5813bbbc4bcd9fc52f0591a3196e52aa7d8c40"

def test_teamsfx_tasks_match_pinned_provider_metadata():
    raw = (ROOT / "tests/fixtures/toolkit-package.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == METADATA_SHA256
    package = json.loads(raw)
    definition = next(d for d in package["contributes"]["taskDefinitions"] if d["type"] == "teamsfx")
    validator = Draft7Validator(definition["properties"]["command"])
    tasks = json.loads((ROOT / ".vscode/tasks.json").read_text())["tasks"]
    for task in tasks:
        if task["type"] == "teamsfx":
            assert validator.is_valid(task["command"]), f"Unsupported pinned Toolkit task command: {task['command']}"
    assert not validator.is_valid("publish"), "Upstream contract changed; re-review dispatch"
