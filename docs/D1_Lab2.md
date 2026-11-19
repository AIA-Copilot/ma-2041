# D1_Lab2 — API action and Adaptive Card contract

**Learning outcome:** Implement a ticket lookup API operation, change an Adaptive Card label, and trace how the declarative action consumes API data. List filtering, card structure and manifests are supplied. The Python API supports a declarative agent; it is not a replacement for the declarative agent.

**Planned practice:** 45 minutes, excluding setup and provider support.

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

## Tasks (5 + 10 + 10 + 12 + 8 minutes)

### 1. Start from a bounded reference (5 min)
```powershell
Copy-Item starters\lab2_3\app.py starters\lab2_3\app.py.before-D1-02 -Force
Copy-Item solutions\lab2_3\app.py starters\lab2_3\app.py -Force
```
Read `public_view`, `list_tickets`, `get_ticket` and `build_adaptive_card`. List filtering and card layout are precompleted. In **only** `get_ticket`, replace the executable body with `raise NotImplementedError("D1-02 get_ticket")`. Keep its decorator/signature. Run:
```powershell
$env:LAB_IMPL = "starters"
python -m pytest tests\lab2_3 -q -k "get_known or get_unknown"
```
Expected: selected tests fail with your deliberate NotImplementedError. Use the selector shown above; it matches the supplied test names.

### 2. Implement the operation (10 min)
In `starters\lab2_3\app.py`, replace that raise with logic that searches `load_tickets()` for an exact ID. If absent, `abort(404)`; otherwise `return jsonify(public_view(ticket))`. Do not return the raw fixture. Use this body inside `get_ticket` (four-space indentation); retain the existing decorator and signature:

```python
    ticket = next((t for t in load_tickets() if t["id"] == ticket_id), None)
    if ticket is None:
        abort(404)
    return jsonify(public_view(ticket))
```

Rerun the same command: both known-ticket and unknown-ticket checks should pass. The response has id/title/body/status/assignee_group; `restricted` is deliberately omitted.

### 3. Edit the card and test its contract (10 min)
In `build_adaptive_card`, change the FactSet label `Owning group` to `Support owner`; keep its value bound to `ticket["assignee_group"]`. Retain version `1.5`, TextBlocks and wrapping. Run the complete checkpoint:
```powershell
python -m pytest tests\lab2_3 -q
@'
from starters.lab2_3.app import app
c=app.test_client()
card=c.get('/tickets/T-1001/card').get_json()
assert any(
    f['title']=='Support owner'
    for b in card['body'] if b['type']=='FactSet'
    for f in b['facts']
)
print('custom card label PASS')
'@ | python -
```
Expected: tests pass, no schema skip, and `custom card label PASS`. The local schema is `fixtures\adaptive_card_schema.json`. The custom probe is needed because the existing tests do not assert your chosen label.

### 4. Observe the API over loopback (12 min)
Run the server in this terminal:
```powershell
python starters\lab2_3\app.py
```
In a second PowerShell window:
```powershell
Invoke-RestMethod http://127.0.0.1:5000/tickets/T-1001 | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/tickets/T-1001/card | ConvertTo-Json -Depth 10
try {
    Invoke-RestMethod http://127.0.0.1:5000/tickets/T-9999
} catch { [int]$_.Exception.Response.StatusCode }
$r = Invoke-RestMethod 'http://127.0.0.1:5000/tickets?status=open'
$r.value | Select-Object id,status
if ($r.value.id -contains 'T-1004') { throw 'restricted list leak' }
if (@($r.value | Where-Object status -ne 'open').Count) { throw 'status filter broken' }
```
Expected: T-1001 JSON without `restricted`, a card with `Support owner`, numeric 404, and only open unrestricted list entries. Stop the server with Ctrl+C. **Do not expose this API:** direct ID and card routes still lack identity/authorization and can disclose restricted fixture records. List filtering is not complete API security; D1_Lab3 addresses the separate secured implementation.

### 5. Trace the declarative action (8 min)
Open the reference files under `solutions\lab2_3\appPackage`: follow `manifest.json` → `declarative-agent.json` actions → `ai-plugin.json` runtimes → `openapi.json` operation IDs. In plugin `response_semantics`, locate `data_path` and `static_template`. Explain why Copilot renders the static template rather than calling `/card`. Your local label edit does **not** change that template. Do not regenerate all manifests: that would touch unrelated exercise files.
At the Code root, save your repaired file:

```powershell
Copy-Item starters\lab2_3\app.py starters\lab2_3\app.py.good-D1-02 -Force
```

In `starters\lab2_3\app.py`, temporarily change the card version to `1.9`, and run:
```powershell
python -m pytest tests\lab2_3 -q -k adaptive_card
```
Expected: failure of the explicit `version == '1.5'` assertion (do not claim this proves schema rejection). Restore:
```powershell
Copy-Item starters\lab2_3\app.py.good-D1-02 starters\lab2_3\app.py -Force
python -m pytest tests\lab2_3 -q
```

## Troubleshooting and recovery
From `Day1`, restart from the original saved exercise:
```powershell
Copy-Item starters\lab2_3\app.py.before-D1-02 starters\lab2_3\app.py -Force
```
For a complete reference recovery (record **assisted**, not independent completion):
```powershell
Copy-Item solutions\lab2_3\app.py starters\lab2_3\app.py -Force
$env:LAB_IMPL = "starters"
python -m pytest tests\lab2_3 -q
```
Import failure: stop the clock and use the setup steps in D1_Lab1, not ad-hoc dependency upgrades. Unexpected green before repair: check `$env:LAB_IMPL` and the file you edited. Save files, rerun; do not weaken tests. Close a previous server with Ctrl+C before opening another. Preserve your edited file before taking recovery.

## Record your results
Save the edited file/diff, exact commands, exit codes, negative/red output and final green output. Record elapsed minutes and `independent` or `assisted`, plus your explanation of the decision being tested. Mark `LOCAL VERIFIED` only after observing the checkpoint; otherwise `NOT EXECUTED` or `FAILED`. Use actual test totals, not a prewritten count. A skipped test does not prove its check.


## Completion checklist

- [ ] Known and missing ticket checks pass after your lookup implementation.
- [ ] The local card has Support owner; tests have no schema skip.
- [ ] Loopback responses and restricted-list filtering match expectations.
- [ ] The wrong card version fails; the restored version passes. You can distinguish the API card from the plugin static template.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
