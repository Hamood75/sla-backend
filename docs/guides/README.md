# Pay-IT integration guides

These guides explain how merchants and partner teams can accept payments through
Pay-IT. They are written for readers who understand basic web concepts such as
URLs, HTTP requests, JSON, and API keys but may not work as full-time software
developers.

## Start here

| What you want to do | Guide |
|---|---|
| Connect your website, app, ERP, or billing system directly to Pay-IT | [Direct API integration](direct-api-integration.md) |
| Receive reliable payment updates on your server | [Webhooks](webhooks.md) |
| Create and safely manage integration credentials | [API credentials](api-credentials.md) |
| Create shareable links or add modal, inline, and redirect hosted checkout | [Payment Links](payment-links.md) |

## AI-assisted integration

The [`payit-integration` AI-agent skill](skills/integration/SKILL.md) can assess an existing codebase and implement the appropriate Pay-IT flow in its programming language and framework. It defaults to hosted checkout unless the user explicitly requires direct server-to-server payment initiation. It begins by asking about the business purpose, test or live mode, required payment features, webhook needs, target application, and acceptance criteria. It must then present its implementation plan and receive explicit user approval before changing the target project.

See the [AI-agent skills index](skills/README.md) for installation and usage guidance.

## Integration choices

### Direct API integration

Your server sends a payment request to Pay-IT using an API key. Pay-IT queues
the mobile-money payment and returns a `payment_id`. Your server then checks the
payment status or waits for a signed webhook.

Choose this when you have a backend system and want to create payments from
your own application.

### Payment Links and hosted checkout

The merchant creates a reusable Payment Link. A customer can open the public link,
use checkout in a merchant-site modal, or pay through an inline hosted frame. The
hosted JavaScript SDK supplies the supported modal, inline, and redirect integration.

Choose this when you want a shareable payment page, an embedded checkout, or do
not want your own server to collect the payer's mobile number.

## Production API

```text
https://app.payit.co.tz
```

All production requests must use HTTPS. The examples in these guides use the
production host. Replace identifiers, credentials, amounts, phone numbers, and
URLs with your own values.

## Three types of credentials

The platform uses different credentials for different purposes.

| Credential | Used by | Header |
|---|---|---|
| Merchant JWT | The signed-in merchant dashboard | `Authorization: Bearer <jwt>` |
| Integration API key | The merchant's backend system | `X-PayIt-Api-Key: <key>` |
| Checkout token | A public hosted-checkout browser session | `Authorization: Checkout <token>` |

Never substitute one credential type for another. Never put an integration API
key or webhook secret in browser JavaScript, a mobile application, a public Git
repository, screenshots, or customer-facing logs.

## JSON naming conventions

Pay-IT currently has two JSON naming conventions:

- Merchant dashboard and authenticated customer endpoints use `PascalCase`,
  for example `PaymentLinkId` and `MerchantId`.
- Public checkout, direct integration, and webhook payloads use `snake_case`,
  for example `payment_link_id` and `merchant_reference`.

Property names should be sent exactly as shown in each guide.

## Money, dates, and phone numbers

- Currency is currently `TZS`.
- Public and integration API amounts are decimal strings such as `"50000.00"`.
- Dates and times use UTC ISO 8601, for example `2026-08-12T10:30:00Z`.
- Tanzanian mobile numbers should be normalized to `255XXXXXXXXX`, for example
  `255754123456`.

## Asynchronous payments

A `202 Accepted` response means that Pay-IT has durably queued the payment. It
does **not** mean the payer has completed payment.

After receiving `202`:

1. Save the returned `payment_id`.
2. Show a processing state to the user.
3. Poll the appropriate status endpoint or process Pay-IT webhooks.
4. Fulfil an order only when the status becomes `succeeded`.

Do not create a second payment merely because a request timed out or returned a
temporary server error. The first request may still be processing.

## Common HTTP responses

| HTTP status | Meaning | Recommended action |
|---:|---|---|
| `200` | Read or dashboard operation succeeded | Process the response. |
| `201` | Checkout session created | Save all display-once checkout credentials. |
| `202` | Payment or attempt queued | Poll status; do not treat it as paid. |
| `400` | Invalid request | Correct the data before retrying. |
| `401` | Missing, expired, or invalid credential | Authenticate again or replace the credential. |
| `403` | Valid credential without required permission, scope, or environment | Correct permissions or headers. |
| `404` | Resource unavailable or intentionally hidden | Check the public identifier and tenant ownership. |
| `409` | State, version, active-attempt, or idempotency conflict | Read current state before taking another action. |
| `429` | Rate limit reached | Retry with bounded backoff and the same idempotency key. |
| `500`/`503` | Temporary platform failure | Check status before creating any replacement payment. |

Merchant Payment Link endpoints do not yet emit the full status range. Most conflict and not-found conditions currently arrive as `400`; `webhook/configure` is the exception and returns `403`, `404`, and `409` accurately. Branch on `ResponseCode` rather than HTTP status alone for merchant endpoints.

## Source of truth

These guides summarize the implemented API as of 19 August 2026, verified against
the deployed core-engine source rather than the specification alone. The
canonical machine-readable contract remains:

```text
Backend/api/core-engine/api-docs/spec.yaml
```

When a guide and the deployed API appear to disagree, record the request ID,
HTTP status, safe response body, endpoint, and time, then contact Pay-IT support.
Do not include API-key secrets, webhook secrets, or full payer phone numbers.
