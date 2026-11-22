# Currency lab: instructor acceptance

## Verified outside the learner VM

The browser made anonymous requests with credentials omitted and no API key:
- `GET /v2/rate/USD/CAD`: HTTP 200, correct base/quote, positive numeric rate and effective date.
- `GET /v2/rate/EUR/GBP`: HTTP 200, same response contract.
- `GET /v2/rate/USD/CAD?date=2024-01-02`: HTTP 200, historical response dated 2024-01-02.
- `GET /v2/rate/USD/ZZZ`: HTTP 422, invalid currency error.

The supplied OpenAPI 3.0.3 document passes the official OAS JSON schema. Both plugin checkpoints pass Microsoft's v2.4 plugin schema. The card passes the Adaptive Card JSON schema. All three live success bodies match the supplied response contract.

The card was rendered at a narrow width with AdaptiveCards JS 2.11.3 after explicit substitution of the four field tokens. It had no renderer validation errors and no visible clipping. This is not a Copilot screenshot and not a full Adaptive Cards templating-engine test. An attempted standalone templating-engine preview could not load its expression dependency; no learner setup depends on that tool.

## Still to run in the assigned MS-4018 VM

1. Record the installed Agents Toolkit version, PowerShell version, assigned tenant and available agent-upload permissions privately.
2. Run the learner guide exactly from its supplied files. Do not substitute a previously provisioned project or skip the no-card stage.
3. Capture evidence of Toolkit provisioning and a real Copilot action invocation. Confirm the historical query is passed, and compare the returned pair/date/rate with the service response.
4. Open the action citation and verify the embedded card renders. Check the narrow-pane layout and the heading-change exercise.
5. Check unsupported currency and transfer requests. Confirm no invented successful payment.
6. Time the whole run. The 45–60 minute budget is an estimate, not an observed duration.

Mark each checkpoint Pass / Fail / Not run. The package is finalized for instructor rehearsal, not certified as an end-to-end tested tenant lab. A functioning browser request does not establish that Copilot can invoke the API through this tenant's policy.

## Delivery boundaries

This package covers Day 1 section 2 only. It replaces the proposed local restaurant/Camp backend route for API actions and cards, not section 3's separate synced connector or section 4's WIQD lab. Do not direct students through the old public D1_Lab2/D1_Lab3 restaurant instructions as well.

No authentication, backend, tunnel or Azure deployment is required. Provision only the new declarative agent using the training account. Do not promise agent installation rights solely because the user can open Copilot Chat. If policy blocks creation or upload, obtain the training tenant administrator's help.

The public Frankfurter service has no uptime SLA. Recheck the teaching currency pair shortly before class. If the service is down, use `sample-rate.json` for file/card explanation only and mark live tests unperformed. No paid fallback or external deployment is authorized.

Frankfurter describes its default blended rates as usable commercially. The lab uses those default routes, not provider-specific endpoints with separate provider terms. The default rates may change as source data arrives; never hard-code an expected latest value. Credit: https://frankfurter.dev/
