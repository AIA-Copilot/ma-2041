# Lab 1 assets — FirstAgent

Follow the complete [learner guide](../../docs/D1_Lab1.md). Keep this course repository in the left VS Code window. Install Toolkit as described in Lab 1, then use its default project folder to create `C:\Users\Admin\AgentsToolkitProjects\ZavaLab1` in a separate right-hand window. This asset folder is not an installable app or a pre-provisioned project.

## Current exercise

The learner guide builds **Zava Learning Agent** using **WebSearch** scoped to `https://learn.microsoft.com`. Learners deploy and test the first version, add three `conversation_starters`, increment the app version in source `appPackage/manifest.json`, provision Dev again, and test the updated agent. Use the default installed Toolkit; no prerelease or preview switch is required by these instructions.

No document import is part of the revised lab. The retained ZAVA-FACTS.md, Word document, flow-embed.png and upstream snapshot are historical source assets, not current learner steps. Do not use them as evidence that embedded knowledge works in the training tenant. Original source files and their license remain unchanged.

## Source, permission and attribution

Source: Microsoft Corporation, [Microsoft Copilot Camp](https://github.com/microsoft/copilot-camp), commit `937fd5b6af4c705597381dd24d5e8aa7693521ad`.

The pinned repository's [MIT license](upstream/LICENSE) permits copying, modification and redistribution of the software and associated documentation, provided the copyright and permission notice accompany copies/substantial portions. That license is preserved verbatim. No separate rights override was found in the selected instructional Markdown or document body. Zava is fictional training content, not an endorsement or real support service.

These upstream files were selected and downloaded without byte changes; paths below are relative to `upstream/` and match the pinned repository:

- `LICENSE` — copyright and redistribution permission.
- `docs/pages/extend-m365-copilot/01-first-agent-toolkit.md` — exact selected instructional source.
- `docs/assets/docs/extend-m365-copilot-09/Zava New Hire Logistics.docx` — historical embedded-knowledge input.
- `docs/assets/images/extend-m365-copilot-09/flow-embed.png` — capability illustration referenced by that source.
- `docs/assets/images/01-first-agent-toolkit/demo-e1b.png` — example answer screenshot referenced by that source; not evidence of learner success.

The [archival source](upstream/docs/pages/extend-m365-copilot/01-first-agent-toolkit.md) retains its original site widgets, include directive, external telemetry image URL and navigation to unbundled site pages. It is an exact provenance snapshot, **not the runnable learner guide**. Do not render it as a course web page or follow its preparation/admin steps. Its sample-document and Markdown screenshot links resolve locally; the rest of the website is intentionally not mirrored.

## Adaptation decisions

Scott requested the web-search replacement after DOCX and PDF embedded-knowledge attempts failed to retrieve content in the training tenant. The cause remains unconfirmed. The revision teaches a complete build/test/iterate loop without changing the installed Toolkit version. It preserves VM setup, left/right VS Code windows, No Action creation and the Dev provisioning checkpoint. Learners check answers and sources directly in Copilot; no manual test-record file is required. Attribution was removed from the learner guide at Scott's request; original license/provenance remains in this source folder.

Authoring reference: [Microsoft declarative agent manifest](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-manifest-1.9), including WebSearch and conversation_starters. The lab preserves the template-generated schema; it does not ask learners to upgrade it. Static schema checks and PDF review are separate from live tenant rehearsal. Web-search policy, actual answers and conversation-starter rendering still require the real lab account.
