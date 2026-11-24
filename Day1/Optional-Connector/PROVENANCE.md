# Source identity and bounded adaptation

- Upstream: Microsoft [Copilot Camp E7](https://microsoft.github.io/copilot-camp/pages/extend-m365-copilot/07-add-graphconnector/).
- Repository: `microsoft/copilot-camp`.
- Exact commit: `937fd5b6af4c705597381dd24d5e8aa7693521ad`.
- Source directory: `src/extend-m365-copilot/path-e-bonus-gc-lab/trey-feedback-connector`.
- Downloaded **39 complete project files**, plus the repository-root MIT [LICENSE](LICENSE). `UPSTREAM-MANIFEST.json` records source paths and SHA-256 hashes **before** adaptation. No source-tree subset was silently substituted.
- The five upstream feedback Markdown documents have been replaced by explicitly fictional Zava travel documents, retaining CF-001 through CF-005 as stable IDs/filenames. Original bytes are preserved in the internal zava-travel-continuity-2026-11-22/originals packet; UPSTREAM-MANIFEST.json remains the historical baseline. Repository LICENSE is MIT; upstream `package.json` retains its original `ISC` metadata rather than silently rewriting provenance. Dependencies carry their own licenses.

## Necessary changes

1. `src/functions/connections.ts`: removed registration of `retractConnection` entirely. Important finding: upstream already had `runOnStartup: false` for retraction, but it remained registered on the same annual schedule as deployment. The adapted host cannot schedule that destructive handler; its original function and Graph delete implementation remain as reference, not a learner command. Deploy still runs on local Development startup and on its original annual timer if someone leaves the host running.
2. `src/services/itemsService.ts`: append `.md` when constructing document URLs. The supplied environment example now uses `https://github.com/AIA-Copilot/ma-2041/blob/main/Day1/Lab3-CopilotConnector/connector/content/`. No content API/server is needed. These new citation destinations require publication and a fresh reachability check; the old upstream HTTP results do not validate them.
3. `src/config.ts`: reject combined connection IDs outside 1–32 alphanumeric characters before any handler writes. The existing environment suffix behavior is preserved.
4. `package.json` / `package-lock.json`: remove only project-local `azure-functions-core-tools`; use the one-time global v4 installer instead. Regenerate the lock without lifecycle scripts, audit repair or dependency modernization. Other source dependency versions remain pinned by the supplied lock.
5. `.vscode/tasks.json`: remove lesson-time installation tasks, compile before starting the globally installed Functions host with debugger port 9229, and explicitly prepend the portable Windows Node 22 location to each task's Path. Workspace must be `connector/`; `../../../tools` resolves to repository tools.
6. Preserve original `teamsapp.yml` and `teamsapp.local.yml` byte-for-byte under `upstream-reference/`. Active current-name `m365agents.local.yml` and `m365agents.yml` use only the original local registration/settings flow, with single-tenant app creation matching the original Entra manifest. No ARM deployment, tunnel, Azure resource or API plugin is in the active lifecycle. Retained `infra/` files are provenance, not an instruction to deploy.
7. `.gitignore`: also ignore per-learner `env/.env.local`. Existing secret-user-file and local-settings exclusions remain. Added `.env.local.example` contains no credentials.
8. `tsconfig.json`: set `types: ["node"]` to isolate compilation from unrelated ancestor Bun ambient types encountered in the verification environment. Plain build initially failed on those external types; after this bounded setup correction it passes without `skipLibCheck`.
9. Add offline verification, setup, guide and provenance documents. The Zava conversion changes content and renames `consultant` to `owner` consistently in the item model, parser, adapter, schema, search card and card fixture. Graph algorithms, ACLs, permissions and lifecycle remain unchanged. A fresh connection is required: the sample does not migrate an existing schema/card.

## Inspected runtime behavior and limitations

The handler ensures/creates an external connection, ensures its schema, patches initial search-result settings, reads local `./content`, maps each Markdown file to text plus properties, then PUTs each stable item ID to Graph. Authentication uses upstream DefaultAzureCredential configured with the locally generated app credentials. Provisioning writes credentials into ignored local files. Each item ACL is `everyone`, so synthetic content is mandatory.

Repeated ingestion overwrites the same IDs; it does not reconcile deletion of removed local files. Stopping local tasks leaves tenant resources intact. Upstream `loadContent` catches/logs per-item failures, so `Loading` or an invocation-success line alone is not proof of ingestion. Schema error handling/polling is retained, including its retry limitations; the guide requires portal/search evidence instead of inferring readiness. Admin consent may exceed the sample's ten-minute connection timeout. No production reliability or security guarantee is claimed.

No previous E2–E4 API project is downloaded or required. The student extends the existing Lab 1 ZavaLab1 **No Action** agent, retaining WebSearch and adding the actual connection ID. The instruction file is replaced to permit grounded fictional company-policy answers, and the same app is versioned and reprovisioned. GitHub citation links are public source references, not an API runtime.

## Verification boundary

For the Zava source conversion, run `npm run build` and `node scripts/verify-offline.cjs` with already-prepared dependencies. The internal continuity packet REPORT.md records current source checks. DELIVERY-MANIFEST.json is also a historical pre-Zava inventory pending release regeneration; neither historical file certifies these edited bytes.

`VERIFICATION.json` is historical pre-Zava evidence, not verification of the current content. It contains actual Node 22.22.2 Linux/WSL install, compilation, offline transformation/registration checks and source-link HTTP results. Dependency installation fetched packages with scripts disabled; compilation and the mock-based tests used no tenant or Functions host. The offline test asserts exactly five items, source-link mapping, the ACL, invalid-ID rejection and only the deploy timer registration. It does not execute a timer handler.

**Not run:** Windows VS Code/F5, actual Core Tools/Azurite startup, tenant login, app registration, consent, Graph ingestion, indexing, or a live cited Copilot reply. Those remain Scott's VM/tenant rehearsal. Scott's temporary Day 1 dependency-risk acceptance is respected; it is not a Day 2 waiver or production approval.
