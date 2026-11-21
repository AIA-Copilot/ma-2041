# Lab 1 — Briefing Coach

Start with `../../docs/D1_Lab1.md` in the distributed course root (the guide is under `docs`). Work inside the provided MS-4018 VM.

- `generated-baseline/`: real, unmodified WIQD 1.0.0 `plugin create` + `plugin add agent` output. Generated README/tasks mention Toolkit; they are not the instructions for this direct-CLI lab. Do not press F5.
- `assets/`: text and conversation starters to apply to your new project.
- `finished/`: the real scaffold with only the instruction text and declarative-agent description/starters edited. Native WIQD source validation passed. This is a recovery checkpoint, not a provisioned app.
- `check-source.mjs`: independent local content checks. These do not replace WIQD validation.
- `TEST-RECORD.md`: your acceptance record.

The CLI is pinned to `@microsoft/wiqd@1.0.0`; Node must be 24.15.0 or later. The plugin interface is alpha even though the package is 1.0.0. No coding assistant, Python, Azure subscription, tunnel or API server is used.

No installable app ZIP is supplied: WIQD refuses offline packaging when `copilotAgents` is present. The authorized tenant rehearsal must provision first and then package. No tenant credentials or consent state are included here.
