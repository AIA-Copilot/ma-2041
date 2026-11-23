import json, re
from pathlib import Path
import yaml
from jsonschema import Draft7Validator
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests/fixtures"
schema = json.loads((EVIDENCE / "lifecycle-v1.12.schema.json").read_text())
for file in ("m365agents.yml", "m365agents.local.yml"):
    Draft7Validator(schema).validate(yaml.safe_load((ROOT / file).read_text()))
    print(file + ": schema PASS")
manifest = (ROOT / "appPackage/manifest.json").read_text()
manifest = re.sub(r"\$\{\{(?:TEAMS_APP_ID|BOT_ID)\}\}", "11111111-1111-4111-8111-111111111111", manifest)
manifest = re.sub(r"\$\{\{LAB_\w+_URL\}\}", "https://example.com/lab", manifest)
mschema = json.loads((EVIDENCE / "teams-v1.30.schema.json").read_text())
Draft7Validator(mschema).validate(json.loads(manifest))
print("Manifest with synthetic substitutions: schema PASS (not tenant/package validation)")
