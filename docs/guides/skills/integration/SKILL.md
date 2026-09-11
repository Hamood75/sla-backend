---
name: payit-integration
description: Assesses an existing application, defaults to the Pay-IT hosted checkout JavaScript SDK unless direct API payment initiation is explicitly required, presents an implementation plan for explicit user approval, and implements Payment Links, modal or inline checkout, redirects, signed webhooks, or direct mobile-money payments in test or live mode. Use when a user asks an AI agent to integrate Pay-IT into a website, backend, mobile application, ERP, billing platform, or other codebase.
---

# Pay-IT Integration

Use this skill to take a Pay-IT integration from requirements discovery through implementation and verification in the user's existing codebase.

## When to use this skill

Use it when the user wants to:

- accept instant mobile-money payments through the direct API;
- create or consume Payment Links;
- add Pay-IT hosted checkout to a website or application;
- receive and verify Pay-IT webhook events;
- combine payment initiation, status polling, and webhooks;
- move an existing Pay-IT integration from test mode to live mode;
- diagnose or complete an incomplete Pay-IT integration.

Do not use it merely to explain an API endpoint. For an explanation-only request, answer from the appropriate guide without changing the user's code.

## Sources of truth

Before designing or editing an integration, read the relevant guide completely:

- `../../README.md` for shared conventions and integration choices;
- `../../api-credentials.md` for API-key creation, scopes, rotation, and revocation;
- `../../direct-api-integration.md` for server-to-server mobile-money payments and status polling;
- `../../webhooks.md` for webhook configuration, signatures, retries, and replay;
- `../../payment-links.md` for Payment Links, public checkout, guest payments, and logged-in checkout.

Resolve these paths relative to this `SKILL.md`. If the guides are not available at those paths, locate them in the repository before proceeding. Treat the current machine-readable API specification, when present, as the final contract authority. In the Pay-IT repository it is `Backend/api/core-engine/api-docs/spec.yaml`.

Never invent an endpoint, field, enum, scope, response, or retry rule. If the guide and machine-readable contract disagree, stop and report the conflict before implementing.

The guides were verified against the deployed core-engine source on 19 August 2026. `spec.yaml` remains the contract authority; where a guide and the specification disagree, report the conflict rather than choosing one.

## Mandatory first step: integration interview

Before inspecting or changing the target codebase, ask the user for the information below. Combine the questions into a concise questionnaire, and do not ask for secrets to be pasted into chat.

1. **Business purpose:** What product or workflow is being integrated, and what should a successful payment accomplish?
2. **Environment:** Is this a test-mode integration, a live-mode integration, or a test-to-live migration?
3. **Integration features:** Which are required?
   - Payment Links or the hosted checkout JavaScript SDK (**default and recommended**);
   - direct server-to-server mobile-money initiation (**only when explicitly required**);
   - signed webhooks;
   - payment-status polling;
   - a combination of these.
4. **Target application:** Which repository or directory should be changed? Which component should own the integration: backend, frontend, mobile app, or more than one?
5. **User journey:** Who initiates payment—an anonymous guest, a logged-in Pay-IT customer using a saved account, or the merchant's server? For a website, should checkout open as a modal, appear inline, or redirect to a full page?
6. **Payment details:** Which mobile networks, currencies, amount rules, merchant references, and payer-purpose fields are needed?
7. **Webhook needs:** Which public HTTPS callback URL and event types should be used? If the URL is not ready, ask whether to implement the receiver first and leave configuration as a documented deployment step.
8. **Credentials and deployment:** Are the required test or live credentials already provisioned in a secret manager or environment configuration? Ask only where they will be supplied, never for the secret value itself.
9. **Acceptance criteria:** What observable result will confirm the integration is complete?

For modal or inline checkout, also ask for the exact test and live website origins, such as `https://shop.example.com`. Do not accept a URL path, wildcard domain, or guessed deployment origin. For standalone redirect checkout, ask whether the merchant needs configured success and failure return pages.

If the user has already supplied an answer, do not ask for it again. If a missing answer materially changes security, architecture, or live behavior, wait for the answer. Otherwise state a conservative assumption and continue. When the payment-initiation method is missing or ambiguous, explicitly state that hosted checkout will be used by default.

## Safety rules

- Never place a merchant API key, webhook secret, checkout token, or other server credential in frontend or mobile source code.
- Direct API calls must originate from a trusted backend. A browser or mobile application calls the user's backend, which then calls Pay-IT.
- Store secrets through the target project's established environment or secret-management mechanism. Commit only variable names and safe examples.
- Never log full API keys, webhook secrets, checkout tokens, one-time checkout challenges, unmasked mobile numbers, or raw sensitive payloads.
- Never create a real live charge as a test unless the user explicitly authorizes the amount, payer, and timing.
- In live mode, use read-only or mocked verification until the user explicitly authorizes a controlled real-payment test.
- Use a stable idempotency key for every payment-creation operation and preserve it across safe retries.
- Treat payment creation as asynchronous. An accepted request is not proof of successful payment.
- Treat `SUCCEEDED` as the authoritative successful terminal state. Do not infer success from an HTTP `202`, a mobile prompt, or a gateway dispatch.
- Verify webhook signatures against the exact raw request body before parsing or acting on the event.
- Process webhook event IDs idempotently because deliveries can be duplicated or arrive out of order.
- Keep a rotated webhook secret accepted until every pre-rotation delivery has exhausted its retries, not merely until the advisory 24-hour timestamp. Deliveries are signed with the secret held when they were queued.
- Treat a `200` from the receiver's host as proof of delivery only when it came from the receiver route itself. A misconfigured path can return `200` from an unrelated page handler while the receiver never executes.
- Follow every `AGENTS.md`, `CLAUDE.md`, repository policy, ownership boundary, and approval gate found in the target codebase.
- Preserve unrelated user changes. Do not perform destructive Git or filesystem operations.

## Phase 1: assess the target codebase

After the interview, inspect the target application before proposing changes.

1. Locate and read repository instructions such as `AGENTS.md`, `CLAUDE.md`, and relevant local skills.
2. Identify the programming language, framework, dependency manager, runtime version, and application entry points.
3. Determine whether the target is a monolith, API service, serverless application, frontend, mobile app, or multi-service system.
4. Find existing patterns for:
   - HTTP clients and timeouts;
   - configuration and secret injection;
   - controllers, routes, services, and dependency injection;
   - persistence and migrations;
   - background jobs or queues;
   - logging and sensitive-data redaction;
   - tests, mocks, and fixtures;
   - error mapping and API responses.
5. Search for existing Pay-IT code, payment providers, idempotency handling, webhook receivers, payment records, and status state machines.
6. Identify the smallest safe integration boundary. Reuse the application's established architecture rather than adding an unrelated pattern.
7. Determine whether schema changes are needed to persist:
   - merchant reference and Pay-IT `payment_id`;
   - idempotency key;
   - current payment status and failure category;
   - processed webhook event IDs;
   - timestamps and reconciliation information.
8. Run the existing relevant tests or static checks before editing when practical, so pre-existing failures are distinguishable from integration failures.

Summarize the assessment for the user, including the proposed files, risks, assumptions, and verification approach. If the target repository requires approval before significant changes, wait for it.

## Integration decision tree

Choose the implementation from the answers and the codebase assessment.

### Default selection rule

Prefer **Payment Links through the hosted checkout JavaScript SDK** for every new website integration. Select SDK `modal` mode by default. Select `inline` when the user explicitly wants checkout displayed within a named page region, and select `redirect` when framing is unsuitable or the user wants a full-page handoff. Select hosted checkout when the user asks generally to “accept payments,” requests webhooks without naming an initiation method, is unsure which approach to use, or provides requirements that either approach could satisfy.

Select the **direct API** only when the user explicitly requires Pay-IT payment initiation from their trusted server. Valid explicit requirements include a direct server-to-server integration, a merchant-controlled payment API, or a clear instruction to use `POST /api/integrations/v1/mobile-money-payments`.

Do not infer permission to use the direct API merely because:

- the target application has a backend;
- the merchant wants an instant or seamless experience;
- the merchant wants a custom user interface;
- webhooks or status polling are required;
- direct API integration appears technically convenient.

If the user's wording is ambiguous, present hosted checkout in the implementation plan. If direct API appears necessary, explain why and ask the user to explicitly choose it before including it in the plan.

Webhooks may be added to either approach and do not change the hosted-checkout default.

### Payment Link or hosted checkout

Use this as the default payment-initiation method. For a website, integrate the hosted script from `https://payit.co.tz/sdk/checkout-v1.js` and call `window.PayIt.checkout(options)`. The customer completes payment in PayIt's hosted UI, while the integrating application avoids holding a merchant API key solely to initiate payment.

Implement only the layers the application owns:

1. confirm the Payment Link is published and record its slug;
2. for `modal` or `inline`, configure the exact merchant website origin through `/api/Merchant/v2/payment-links/embed-origins/details` and `/configure`, using the current Payment Link `Version`;
3. load `https://payit.co.tz/sdk/checkout-v1.js` with `defer` and initialize `window.PayIt.checkout({ slug, mode, ...callbacks })`;
4. for `inline`, provide a real CSS selector or DOM element in `container`;
5. call `open()` from the intended user interaction, and retain the instance only when the application needs `close()`, `destroy()`, or `isOpen()`;
6. use `onReady`, `onProcessing`, `onSuccess`, `onFailure`, and `onClose` only to update the user interface;
7. use a verified signed webhook or authenticated server-side status read before fulfilling an order;
8. for `redirect`, configure success and failure targets through the Payment Link redirect management endpoints when return navigation is required;
9. handle an unavailable or unauthorized embed as a generic checkout-unavailable state without probing whether the link or origin exists.

Never construct `/embed/pay/{slug}` manually and never implement a separate raw `postMessage` listener when using the SDK. The SDK generates the `parent_origin`, `instance_id`, and nonce values; creates the sandboxed iframe; validates the PayIt origin, iframe source, channel, version, instance, nonce, and event; bounds resizing; and suppresses duplicate terminal callbacks.

The SDK modes are:

- `modal` — default for a Pay button on a merchant website;
- `inline` — requires `container` and an allowed exact origin;
- `redirect` — navigates to `/pay/{slug}`, does not use an iframe, and does not emit completion callbacks.

If the target is not a browser-based website, prefer a normal Payment Link redirect or deep-link handoff unless the user explicitly requests and can support a secure webview integration.

If the merchant also needs to create and manage links from its own product, use the authenticated `/api/Merchant/v2/payment-links/*` management endpoints from the Payment Links guide.

Use the low-level public checkout endpoints only when the user explicitly requires a custom hosted-checkout implementation that the SDK cannot provide. Record that exception in the plan. In that case:

1. resolve the published link through `GET /api/public/payment-links/{slug}` and render its returned amount rules;
2. create a session with a stable `Idempotency-Key`;
3. keep `checkout_token`, `checkout_challenge`, and `encrypted_transaction_id` out of logs and persistent browser analytics;
4. use the correct guest or logged-in authorization flow;
5. poll only within a bounded UI window and reconcile authoritative completion on the server.

### Direct instant payment

Use only when the user has explicitly required the merchant's trusted server to initiate a mobile-money collection. Record that explicit requirement in the implementation plan.

Implement:

1. a server-only Pay-IT client;
2. API-key injection through secrets/configuration;
3. `POST /api/integrations/v1/mobile-money-payments`;
4. a unique stable `Idempotency-Key` tied to the merchant's payment/order record;
5. persistence of `payment_id`, merchant reference, amount, and status;
6. `GET /api/integrations/v1/checkout-sessions/{sessionPublicId}` for controlled polling or reconciliation;
7. normalized error handling that does not expose Pay-IT credentials or internal payloads;
8. tests for success, pending, failure, timeout, duplicate request, and malformed response.

The API key requires the scopes used by the selected operations, such as `mobile_money_payments:create` and `checkout_sessions:read`. Add `payment_links:read` only if the application reads link configuration.

### Signed webhooks

Use for reliable server-to-server payment completion notifications. Webhooks normally complement, rather than replace, payment initiation.

Implement:

1. a public HTTPS `POST` route;
2. access to the exact raw request bytes;
3. signature verification using the algorithm and headers in `webhooks.md`;
4. timestamp tolerance and secret-rotation handling;
5. durable uniqueness on webhook event `id`;
6. fast `2xx` acknowledgement after safe persistence;
7. asynchronous business processing when work may be slow;
8. state-transition rules that prevent an old or duplicate event from regressing a terminal payment;
9. tests for a valid signature, invalid signature, stale timestamp, duplicate event, replay, and rotated secret.

Webhook configuration uses the merchant management API and a merchant JWT. Receiving webhook events does not use the merchant API key as the signing secret.

#### Configuration lifecycle

`POST /api/Merchant/v2/payment-links/webhook/configure` is version-guarded and has no read counterpart. Handle it as follows.

1. **Configure the full receiver URL, including its path.** A bare origin such as `https://merchant.example` passes validation and delivers to `/`. Many web frameworks answer `POST /` with a `200`, so the delivery looks successful while the receiver never runs. Send the exact path the route is mounted on, for example `https://merchant.example/payit/webhook`.
2. **Send the payment link's current `Version`, and re-read the `Version` the response returns.** Every successful configure increments the link version. The response carries the post-save `Version`; use it for the next versioned call on that link. A stale value fails with HTTP `409` and `ResponseCode` `1124` — refetch `payment-links/details` and retry.
3. **There is no `webhook/details` endpoint.** Unlike `embed-origins` and `redirects`, webhook configuration cannot be read back. An application that shows current webhook state must persist its own record of what it configured. Do not design a settings screen that reads the live configuration.
4. **Map the rejection causes rather than retrying blindly.** `1124` stale version (409); `1125` malformed URL — not absolute HTTPS, or has credentials, query string, fragment, IP-literal host, loopback, `localhost`, or `.local` (400); `1126` host did not resolve, or resolved to a non-public address (400); `1127` empty or unsupported `SubscribedEvents` (400); `1101` link not found (404); `901` missing payment-link management capability (403). Only `1124` is retryable, and only after refetching.
5. **`webhook/test` needs both an `ACTIVE` configured endpoint and at least one existing checkout session.** Its failure message names only the session, so treat "webhook test requires an existing checkout session" as covering either missing precondition, plus permission failures.

#### Secret rotation

Each delivery snapshots its signing secret when it is queued, not when it is sent, and the retry schedule spans roughly 80 hours. A delivery queued moments before a rotation therefore keeps being signed with the **old** secret for its whole retry life — well beyond the 24-hour `PreviousSecretValidUntilUtc` returned by `rotate-secret`.

Implement rotation as:

1. accept both the current and previous secret, trying current first;
2. keep the previous secret until pre-rotation deliveries can no longer arrive — the full retry horizon, not the 24-hour advisory window;
3. never treat `PreviousSecretValidUntilUtc` as the moment it becomes safe to drop the old secret. Pay-IT uses that timestamp only to purge its own stored copy; it does not stop old-secret deliveries from arriving.

Rotating invalidates nothing already queued, so a rotation performed to recover from a leak must be paired with treating in-flight deliveries as signed by the compromised secret.

#### Target stability

Target safety is revalidated on **every** delivery attempt, not only at configuration time. The host must keep resolving to public addresses for the life of the integration. A configuration that succeeded starts failing if DNS changes, the host moves behind a private address, or a development tunnel is recycled. Do not treat a successful configure as a permanent guarantee of deliverability.

### Combined integration

For a production payment integration, prefer:

1. hosted checkout to initiate payment unless the user explicitly requires the direct API;
2. webhooks as the primary completion signal;
3. status reads for user-facing polling and reconciliation;
4. a local payment record as the application's operational history;
5. Pay-IT status as the authority when local and remote state differ.

## Phase 2: design the change

Create and present a concrete implementation plan that covers:

- the user's stated purpose, selected integration features, and acceptance criteria;
- confirmation that hosted checkout is selected by default, or the user's explicit direct-API requirement when direct initiation is selected;
- selected hosted-checkout mode (`modal`, `inline`, or `redirect`), Payment Link slug, exact allowed origins, and standalone return-page requirements;
- selected test or live base URL and configuration names;
- required credential type and least-privilege scopes;
- files and components to add, change, or migrate;
- local payment-state model and transition rules;
- idempotency strategy;
- webhook verification and deduplication strategy, when applicable;
- retry, timeout, and polling behavior;
- frontend/backend responsibility boundary;
- test strategy;
- deployment and rollback steps;
- assumptions, risks, external prerequisites, and intentionally excluded work.

For live mode, explicitly identify any step that could initiate a real payment or change a live webhook destination. Do not execute those steps without clear user authorization.

### Mandatory approval checkpoint

After presenting the plan, stop and explicitly ask the user for permission to proceed with that plan.

The approval request must make clear that permission authorizes the proposed code and documentation changes, but does not automatically authorize a real live payment, live credential creation or rotation, deployment, or modification of a live webhook destination. Those actions require separate explicit authorization when reached.

Accept approval only when the user gives an unambiguous instruction such as “approved,” “proceed with this plan,” or an equivalent clear confirmation. Silence, failure to object, an earlier general request to integrate Pay-IT, or approval of a different plan is not permission to begin implementation.

Before approval, the agent may perform read-only inspection, contract research, and non-mutating diagnostic checks needed to prepare the plan. It must not:

- create, edit, move, or delete project files;
- install, remove, or upgrade dependencies;
- run migrations or change databases;
- change environment configuration or secrets;
- call a Pay-IT endpoint that creates or changes state;
- configure, test, rotate, or replay a webhook;
- deploy or modify external infrastructure.

If the user requests changes to the plan, revise and present the updated plan, then request approval again. Approval applies only to the most recently presented plan. If implementation later requires a material scope or architecture change, pause, present the amended plan, and obtain fresh explicit approval before continuing.

## Phase 3: implement

Enter this phase only after recording the user's explicit approval of the current implementation plan.

Follow the target language and framework's existing conventions. At minimum:

1. Add typed configuration for base URL, credential references, and safe timeouts.
2. Add a narrowly scoped Pay-IT client/service instead of scattering HTTP calls through business code.
3. Model request and response fields with the exact casing and types from the guide.
4. Use decimal-safe handling for monetary values and preserve Pay-IT's string-formatted money values where required.
5. Normalize Tanzanian mobile numbers in the application's validation layer without logging the full number.
6. Propagate or generate correlation IDs while keeping secrets out of telemetry.
7. Persist local state before or atomically with externally visible processing where the architecture permits.
8. Map Pay-IT errors into actionable but non-sensitive application errors.
9. Implement idempotency and concurrency protection before enabling retries.
10. Add focused automated tests using mocked Pay-IT responses and signed webhook fixtures.
11. Add `.env.example` or equivalent safe configuration documentation containing placeholders only.
12. Update the target application's developer and deployment documentation.

For a hosted SDK integration, adapt the generic steps above to the client-only SDK boundary: do not add a server-side Pay-IT client or merchant credential merely to open checkout. Load the hosted script once, initialize one checkout instance for the intended UI, configure exact origins outside public client code, and connect callbacks to presentation state only. Add the merchant's webhook receiver or server-side verification separately when authoritative fulfillment is in scope.

Do not add dependencies when the standard library or an existing project dependency safely meets the requirement.

## Phase 4: verify

Run verification proportional to the change:

1. formatter and static analysis;
2. focused unit tests;
3. relevant integration tests;
4. build or compile check;
5. a contract check against the selected Pay-IT endpoints;
6. for modal or inline checkout, verify the exact configured origin can open the embed and an unregistered origin fails closed;
7. verify SDK close, processing, success/failure UI callbacks, duplicate terminal-event suppression, and redirect fallback as applicable;
8. webhook signature fixtures, when applicable;
9. duplicate and retry scenarios;
10. log inspection to confirm secrets and sensitive values are redacted.

### End-to-end webhook verification

Signature fixtures prove the verification code is correct. They do not prove Pay-IT can reach the receiver. When a real delivery is in scope, verify reachability separately.

1. Expose the receiver on a public HTTPS URL. During development this is normally a tunnel; the tunnel host usually changes on every restart, so treat it as a per-session value rather than a fixed configuration.
2. Configure the payment link webhook with the **full receiver path**, then confirm the configuration call returned `ResponseCode` `0` and record the `Version` it returned.
3. Trigger a delivery and confirm the receiver's own route logged the request. A `200` on a different path means the delivery reached the host but not the receiver.
4. Confirm the receiver returned `2xx` for a valid signature and `401` for a tampered body or wrong secret. A receiver that returns a non-2xx before verifying — for example when its secret is unconfigured — silently discards every delivery, so assert that the secret is actually loaded.
5. Confirm the event was recorded exactly once after a replay of the same event ID.

When the integration target is in the Pay-IT repository itself, `Frontend/payment-links-integration-lab/` provides a ready receiver at `/api/webhooks/payit` that performs signature, timestamp, and duplicate checks and lists accepted deliveries.

Two configuration mistakes account for most "no deliveries" reports, and both present as silence rather than an error: a webhook URL set to a bare origin instead of the receiver path, and an environment variable shadowed by a higher-precedence file — for example a `.env.local` entry that is present but empty overriding a correct `.env` value. Check the value the process actually resolved, not the file you edited.

### Test-mode verification

When test credentials and a reachable test environment are available, execute a controlled test flow after user approval:

1. create or resolve the selected Payment Link;
2. initiate a payment with a unique merchant reference and idempotency key;
3. verify the accepted/pending response;
4. verify webhook receipt or status polling;
5. verify the final local state;
6. replay the same request/event to confirm idempotency.

### Live-mode verification

Default to configuration validation, mocked tests, and read-only checks. Before a real charge, restate the exact amount, account/mobile number ownership, expected outcome, and rollback or reconciliation method, then obtain explicit authorization.

## Phase 5: handoff

Finish with a self-contained report containing:

- what was integrated;
- test or live mode;
- code and documentation files changed;
- required environment-variable or secret names, without values;
- required API-key scopes;
- webhook URL and subscribed events, if applicable;
- commands and tests run with results;
- any live action deliberately not executed;
- deployment order;
- smoke-test and rollback instructions;
- remaining decisions or external prerequisites.

Never claim the integration is complete if credentials, a public webhook URL, database migration, deployment, or end-to-end payment test is still outstanding. Clearly distinguish **implemented**, **verified locally**, **verified in test mode**, and **verified live**.

## Completion checklist

- [ ] Initial integration interview answered
- [ ] Target repository instructions followed
- [ ] Relevant Pay-IT guides and contract read
- [ ] Language and framework assessed
- [ ] Integration boundary and security model agreed
- [ ] Hosted checkout selected by default, or explicit direct-API requirement recorded
- [ ] Hosted checkout mode, Payment Link slug, exact origins, and return-page behavior agreed
- [ ] SDK used instead of a hand-built embed URL or raw message listener
- [ ] Browser callbacks treated as UI signals; authoritative fulfillment remains server-side
- [ ] Complete implementation plan presented to the user
- [ ] Explicit user approval received for the current plan
- [ ] Server credentials kept out of client code
- [ ] Idempotency implemented
- [ ] Async status handling implemented
- [ ] Webhook signature and deduplication implemented when required
- [ ] Webhook configured with the full receiver path, and the returned `Version` recorded for the next versioned call
- [ ] Secret-rotation overlap covers the full retry horizon, not the advisory 24-hour window
- [ ] Real delivery observed on the receiver route, not merely a signature fixture
- [ ] Automated tests added and passing
- [ ] Safe configuration documentation added
- [ ] No secrets or sensitive payer data logged
- [ ] Deployment and rollback documented
- [ ] Verification level reported accurately
