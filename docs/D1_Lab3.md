# D1_Lab3 — Authenticate first, authorize each record

**Learning outcome:** Repair scope and record-level authorization while preserving supplied signature, issuer, audience and expiry validation. Distinguish authentication failures from permission denials. This exercise uses synthetic tokens locally, not a real OAuth sign-in.

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

## Tasks (5 + 12 + 10 + 8 + 5 minutes)

### 1. Load the bounded starting point (5 min)
```powershell
Copy-Item starters\lab4\token_validation.py starters\lab4\token_validation.py.before-D1-03 -Force
Copy-Item solutions\lab4\token_validation.py starters\lab4\token_validation.py -Force
```
Read `validate_bearer_token`, `require_scope`, `authorize_ticket` and `caller_groups`. Leave authentication intact. Replace only the executable bodies of `require_scope` and `authorize_ticket` with `raise NotImplementedError("D1-03 authorization")` (retain signatures). Run:
```powershell
$env:LAB_IMPL = "starters"
python -m pytest tests\lab4 -q -k "required_scope or correct_group"
```
Expected: selected tests fail at the authorization exercise, not missing imports. Tests mint synthetic tokens internally; do not copy keys or tokens into a shell or document.

### 2. Implement the two gates (12 min)
In `require_scope`, test whether the requested `scope` is in `token_scopes(claims)`. Raise `AuthzError` if absent; include the scope name in the message. A valid token with wrong permission maps to **403**, not 401.
In `authorize_ticket`: unrestricted records return normally; restricted records with no `assignee_group` raise `AuthzError`; restricted records allow only when that group is in `caller_groups(claims)`. Otherwise raise `AuthzError`, naming the ticket ID and required group. Never use a query string or message text for groups. The missing-group branch is fail-closed.

### 3. Observe positive and negative cases (10 min)
```powershell
python -m pytest tests\lab4 -v
```
Expected: all Lab 4 tests pass. Read the actual assertions in `tests\lab4\test_secured_api.py` and annotate this matrix:

| Input | Expected API result |
|---|---|
| Genuine fixture token, permitted T-1001 | 200 |
| Genuine Dave token with hr-confidential, T-1004 | 200 |
| Forged/unsigned/expired/wrong issuer/wrong audience | 401 |
| Genuine token missing Tickets.Read | 403 |
| Alice with valid scope, restricted T-1004 | 403, no salaries body |
| Dave HR group, identity-support T-1002 | 403 |
| Correct application API key, restricted T-1004 | 403 |
| No server API key configured | 401 |
| Unknown ticket after authentication | 404 |

These are Flask test-client responses and synthetic-signature checks, **not** Entra OAuth consent. Inspect list filtering: an unreadable restricted record is absent from the list, not merely redacted after delivery.

### 4. Prove the missing-owner branch (8 min)
The existing lab test file does not directly cover every malformed-record case. Run this additional direct check, which prints only synthetic data:
```powershell
@'
from starters.lab4.token_validation import authorize_ticket, AuthzError
try:
    authorize_ticket({'groups': []}, {'id': 'TEST', 'restricted': True})
except AuthzError:
    print('missing owner DENIED as expected')
else:
    raise AssertionError('restricted record without owner was allowed')
'@ | python -
```
Expected: `missing owner DENIED as expected`. To see a genuine red regression, first back up the repaired file:
```powershell
Copy-Item starters\lab4\token_validation.py starters\lab4\token_validation.py.good-D1-03 -Force
```
After this backup, temporarily replace the entire executable body of `authorize_ticket` with `return` (preserve signature), then:
```powershell
python -m pytest tests\lab4 -q -k valid_token_cannot_read_restricted
Copy-Item starters\lab4\token_validation.py.good-D1-03 starters\lab4\token_validation.py -Force
python -m pytest tests\lab4 -q
```
Expected: deliberately broken authorization fails; restored code passes.

### 5. Connect the gates to declarative auth (5 min)
Open `solutions\lab4\appPackage\ai-plugin.apikey.json` and `ai-plugin.oauth.json`. Their runtime auth types are `ApiKeyPluginVault` and `OAuthPluginVault`; `reference_id` is a registration reference, not a secret. Explain why a shared application key cannot stand in for per-user access. Keep all fixture servers private.

## Troubleshooting and recovery
From `Day1`, restart from the original saved exercise:
```powershell
Copy-Item starters\lab4\token_validation.py.before-D1-03 starters\lab4\token_validation.py -Force
```
For a complete reference recovery (record **assisted**, not independent completion):
```powershell
Copy-Item solutions\lab4\token_validation.py starters\lab4\token_validation.py -Force
$env:LAB_IMPL = "starters"
python -m pytest tests\lab4 -q
```
Import failure: stop the clock and use the setup steps in D1_Lab1, not ad-hoc dependency upgrades. Unexpected green before repair: check `$env:LAB_IMPL` and the file you edited. Save files, rerun; do not weaken tests. Close a previous server with Ctrl+C before opening another. Preserve your edited file before taking recovery.

## Record your results
Save the edited file/diff, exact commands, exit codes, negative/red output and final green output. Record elapsed minutes and `independent` or `assisted`, plus your explanation of the decision being tested. Mark `LOCAL VERIFIED` only after observing the checkpoint; otherwise `NOT EXECUTED` or `FAILED`. Use actual test totals, not a prewritten count. A skipped test does not prove its check.


## Completion checklist

- [ ] Your scope and record gates pass the positive and negative matrix.
- [ ] Missing owner is denied; deliberately bypassed authorization fails its test.
- [ ] The repaired file is restored and passes; you can explain 401 versus 403.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
