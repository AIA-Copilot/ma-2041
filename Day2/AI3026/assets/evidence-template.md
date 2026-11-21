# My Day 2 evidence (keep private)

Do not record access tokens, passwords, full generated app settings or environment files.

## Identity chain
- Project endpoint / project name (redact resource prefix in shared evidence):
- Agent name:
- Baseline saved version:
- Grounded saved version:
- Version sent by C# probe and proxy:

## Tests
| Surface | Question | Expected policy section/fact | Actual answer/citation | Pass, fail or blocked |
|---|---|---|---|---|
| Portal before grounding | How long does a standard software request take? | Must not invent a policy | | |
| Portal grounded | How long does a standard software request take? | Section 2: 1–2 business days | | |
| Portal grounded | What is the lunar-office allowance? | Not in document | | |
| C# probe | How do I request custom software? | Section 2: manager + security review | | |
| Teams | How do I request custom software? | Same policy/version as C# | | |
| Copilot | How do I request custom software? | Same policy/version as C# | | |

## Code change
- Input limit before/after:
- Boundary tests changed and actual results:
- Help message change:

## Live gates / cleanup
- Provider approved subscription/tenant and local tunnel:
- Native Windows restore/build:
- Probe real invocation:
- Toolkit provision/deploy:
- Teams actual reply:
- Copilot actual reply (or licensing/policy blocker):
- Host/tunnel stopped:
- Lab-owned resources removed or approved retention:
