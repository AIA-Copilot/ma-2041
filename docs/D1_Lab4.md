# D1_Lab4 — Connector ACLs and safe dry runs

**Learning outcome:** Implement least-privilege connector ACL mapping and inspect the schema, item transform and dry-run lifecycle. Produce a local plan and prove live ingestion is refused. No tenant connection or Azure AI Search service is created.

**Planned practice:** 40 minutes, excluding setup and provider support.

## Starting folder and prerequisites

Continue in the Day 1 VM copy with the Python 3.11 environment and pinned dependencies installed in Lab 1. In VS Code open **File > Open Folder > `C:\ma-2041\Day1`**. Use **Terminal > New Terminal > PowerShell**. All commands below start at this Code root unless a step changes directory.

```powershell
Set-Location 'C:\ma-2041\Day1'
.\.venv\Scripts\Activate.ps1
$env:LAB_IMPL = 'starters'
$env:MA2041_ALLOW_LIVE_INGEST = '0'
if (Test-Path .env) { throw 'STOP: Day 1 requires a clean copy without .env' }
```

If activation is blocked, select `.venv\Scripts\python.exe` with **Python: Select Interpreter** and use `.\.venv\Scripts\python.exe` instead of `python` at the Code root. Use a fresh training shell with no real model, Graph or Entra credentials. Keep all fixture servers on loopback; no tenant writes or tunnels are part of this lab. `LAB_IMPL` selects the implementation for pytest; an explicit script path selects the implementation for a direct command.

## Keep a short lab record

Use your own notes file in the working copy. Record the lab name, changed files, commands, observed outputs/exit codes, positive and negative checks, restored state, and any blocker. Save only fictional data and sanitized screenshots. Never include tokens, keys, passwords, login caches or runtime configuration files. Expected output in this handout is a target to compare against, not proof that your run succeeded.

## Tasks (5 + 10 + 10 + 10 + 5 minutes)

### 1. Start from precompleted payloads (5 min)
```powershell
Copy-Item starters\lab5\connector_client.py starters\lab5\connector_client.py.before-D1-04 -Force
Copy-Item solutions\lab5\connector_client.py starters\lab5\connector_client.py -Force
$env:MA2041_ALLOW_LIVE_INGEST = "0"
```
Setting the gate explicitly to zero overrides any inherited opt-in. Do not add credentials or edit `.env`. Open `build_acl`, `EXTERNAL_GROUP_IDS`, `transform` and `live_allowed`. Replace only `build_acl`'s executable body with `raise NotImplementedError("D1-04 ACL")`, retaining its signature. Run:
```powershell
$env:LAB_IMPL = "starters"
python -m pytest tests\lab5 -q -k acl
```
Expected: ACL-dependent tests fail. Helpers unrelated to the missing function may pass.

### 2. Implement least-privilege mapping (10 min)
Create an empty result list. Iterate only `article.get("acl") or []`. For each source group append exactly `{"type": "externalGroup", "value": EXTERNAL_GROUP_IDS[group], "accessType": "grant"}`. Return the list. Use direct mapping lookup: an unknown group must raise, not become public or everyone. Do not loop over every group in the mapping. Empty source ACL means no grants.

### 3. Check payloads and negative ACLs (10 min)
```powershell
python -m pytest tests\lab5 -v
python starters\lab5\connector_client.py plan
```
Expected: all Lab 5 tests pass. Plan prints transformed item IDs/ACL values and dry-run mode; KB102 grants only `contosohrconfidential`. Compare KB-102 in `fixtures\kb_articles.json` to this output. Inspect supplied schema: properties used by transform must be declared; `version` is integer, `updated` contains a timezone. Do not equate local shape tests with Graph acceptance.
Additional unknown-group probe:
```powershell
@'
from starters.lab5.connector_client import build_acl
try:
    build_acl({'acl': ['unapproved-group']})
except KeyError:
    print('unknown group DENIED as expected')
else:
    raise AssertionError('unknown group did not fail closed')
'@ | python -
```
Expected: the denial message. Existing tests cover empty ACL, no everyone, exact KB-102 mapping and skipped unreachable items.

### 4. Walk the dry-run lifecycle (10 min)
```powershell
python starters\lab5\connector_client.py create-connection
python starters\lab5\connector_client.py register-schema
python starters\lab5\connector_client.py ingest
python starters\lab5\connector_client.py status
$env:MA2041_ALLOW_LIVE_INGEST = "0"
python starters\lab5\connector_client.py ingest --live
$LASTEXITCODE
```
Expected: dry-run commands print intended requests and `[DRY RUN] not sent`; `register-schema` uses PATCH and describes polling to `succeeded`. The deliberately blocked live attempt prints `LIVE REFUSED` and exits 2. Stop immediately if it does not refuse. No requests should be sent by these commands. Do not enable the gate to fix a refusal; refusal is success here.

### 5. Reconcile the connection and explain (5 min)
Compare `CONNECTION_ID` with the D1_Lab1 `CopilotConnectors` connection ID. Explain why a mismatched ID prevents discovery and why a correctly mapped ACL also requires real external group membership provisioning. Write: "payload and ACL verified locally; Graph writes and Copilot discovery NOT EXECUTED." Capture final `python -m pytest tests\lab5 -q` output.

## Troubleshooting and recovery
From `Day1`, restart from the original saved exercise:
```powershell
Copy-Item starters\lab5\connector_client.py.before-D1-04 starters\lab5\connector_client.py -Force
```
For a complete reference recovery (record **assisted**, not independent completion):
```powershell
Copy-Item solutions\lab5\connector_client.py starters\lab5\connector_client.py -Force
$env:LAB_IMPL = "starters"
python -m pytest tests\lab5 -q
```
Import failure: stop the clock and use the setup steps in D1_Lab1, not ad-hoc dependency upgrades. Unexpected green before repair: check `$env:LAB_IMPL` and the file you edited. Save files, rerun; do not weaken tests. Close a previous server with Ctrl+C before opening another. Preserve your edited file before taking recovery.

## Record your results
Save the edited file/diff, exact commands, exit codes, negative/red output and final green output. Record elapsed minutes and `independent` or `assisted`, plus your explanation of the decision being tested. Mark `LOCAL VERIFIED` only after observing the checkpoint; otherwise `NOT EXECUTED` or `FAILED`. Use actual test totals, not a prewritten count. A skipped test does not prove its check.


## Completion checklist

- [ ] The repaired ACL function passes; unknown groups fail closed and empty ACL grants nothing.
- [ ] The plan shows KB102 only grants contosohrconfidential.
- [ ] Dry runs send nothing; the live attempt is refused with exit 2.
- [ ] You can reconcile the connection ID with Lab 1 without claiming Graph ingestion or Copilot discovery.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
