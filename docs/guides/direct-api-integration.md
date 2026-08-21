# Direct API integration guide

Use the direct integration API when your server needs to start mobile-money
payments from an application, website, ERP, school system, billing platform, or
other backend service.

## Before you begin

You need:

1. An approved and active Pay-IT merchant account.
2. A published Payment Link with `AllowApiInitiation` enabled.
3. An API key with the required scopes.
4. A webhook endpoint if you want automatic status notifications.

See [API credentials](api-credentials.md) and [Webhooks](webhooks.md).

## How the payment flow works

1. Your server chooses a published Payment Link.
2. Your server sends a mobile-money payment request with a unique
   `Idempotency-Key`.
3. Pay-IT validates and durably queues the request.
4. Pay-IT returns `202 Accepted` and a public `payment_id`.
5. The payer receives the mobile-money request through the inferred MNO.
6. Your server polls the payment or receives a signed webhook.
7. Your application fulfils the order only after `status` is `succeeded`.

Direct integration payments route to Selcom. Pay-IT infers the provider from the
normalized Tanzanian phone number. The `provider` request field remains required
for backward compatibility but is not trusted as the routing source of truth.

## Base URL and headers

Production base URL:

```text
https://app.payit.co.tz
```

Every integration request requires:

```http
X-PayIt-Api-Key: <full-api-key>
X-PayIt-Environment: test
```

Use `test` with an `mk_test_` key and `live` with an `mk_live_` key.

POST requests also require:

```http
Content-Type: application/json
```

## Idempotency

`POST /api/integrations/v1/mobile-money-payments` requires an
`Idempotency-Key` between 1 and 128 characters.

An idempotency key identifies one logical payment command:

```text
invoice-2026-0042-payment-1
```

- A retry of the same command must reuse the same key and the same payload.
- Reusing the key with different data returns `409 Conflict`.
- A genuinely new payment must use a new key.
- Generate and store the key on your server before sending the first request.

This prevents a network retry from creating a duplicate payment.

## Endpoint summary

| Method | Endpoint | Required scope | Purpose |
|---|---|---|---|
| `POST` | `/api/integrations/v1/mobile-money-payments` | `mobile_money_payments:create` | Create and queue a payment. |
| `GET` | `/api/integrations/v1/payment-links/{paymentLinkPublicId}` | `payment_links:read` | Read a safe Payment Link configuration. |
| `GET` | `/api/integrations/v1/checkout-sessions/{sessionPublicId}` | `checkout_sessions:read` | Read payment status. |

## Read a Payment Link

Use this endpoint to confirm the link is published and API initiation is
allowed before building a payment request.

```http
GET /api/integrations/v1/payment-links/{paymentLinkPublicId}
```

Example:

```bash
curl https://app.payit.co.tz/api/integrations/v1/payment-links/plink_A1B2C3D4E5F6 \
  -H 'X-PayIt-Api-Key: YOUR_API_KEY' \
  -H 'X-PayIt-Environment: test'
```

Success — `200 OK`:

```json
{
  "payment_link_id": "plink_A1B2C3D4E5F6",
  "slug": "idea-school-fees",
  "title": "IDEA School Fees",
  "description": "Pay term fees",
  "amount_mode": "PRESETS_AND_CUSTOM",
  "preset_amounts": ["50000.00", "100000.00"],
  "minimum_custom_amount": "1000.00",
  "maximum_custom_amount": "5000000.00",
  "currency": "TZS",
  "merchant_reference": null,
  "allow_payer_purpose": true,
  "allow_api_initiation": true
}
```

Important fields:

| Field | Meaning |
|---|---|
| `amount_mode` | `PRESETS_ONLY`, `CUSTOM_ONLY`, or `PRESETS_AND_CUSTOM`. |
| `preset_amounts` | Exact permitted preset amounts. |
| `minimum_custom_amount` | Lowest permitted custom amount, when applicable. |
| `maximum_custom_amount` | Highest permitted custom amount, when applicable. |
| `allow_payer_purpose` | Whether a purpose can be supplied. |
| `allow_api_initiation` | Must be `true` for direct payment creation. |

## Create a mobile-money payment

```http
POST /api/integrations/v1/mobile-money-payments
```

Required headers:

```http
X-PayIt-Api-Key: <full-api-key>
X-PayIt-Environment: test
Idempotency-Key: invoice-2026-0042-payment-1
Content-Type: application/json
```

Request fields:

| Field | Type | Required | Rules |
|---|---|---:|---|
| `payment_link_id` | string | Yes | Public ID of a published, API-enabled link owned by this key's merchant. |
| `amount` | decimal string | Yes | Must satisfy the Payment Link's amount rules. |
| `currency` | string | Yes | Currently `TZS`. |
| `mobile_number` | string | Yes | Tanzanian MSISDN; use `255XXXXXXXXX`. |
| `provider` | string | Yes | Compatibility field. The server derives the actual MNO from the number. |
| `merchant_reference` | string or `null` | No | Merchant correlation value, maximum 120 characters. |
| `payer_purpose` | string or `null` | No | Maximum 250 characters and only when allowed by the link. |
| `callback_url` | HTTPS URL or `null` | No | Optional per-request callback constrained to the configured link webhook origin. |

Example:

```bash
curl -X POST https://app.payit.co.tz/api/integrations/v1/mobile-money-payments \
  -H 'X-PayIt-Api-Key: YOUR_API_KEY' \
  -H 'X-PayIt-Environment: test' \
  -H 'Idempotency-Key: invoice-2026-0042-payment-1' \
  -H 'Content-Type: application/json' \
  -d '{
    "payment_link_id": "plink_A1B2C3D4E5F6",
    "amount": "50000.00",
    "currency": "TZS",
    "mobile_number": "255754123456",
    "provider": "MPESA",
    "merchant_reference": "ORDER-42",
    "payer_purpose": "Invoice 42",
    "callback_url": "https://merchant.example/payit/callback"
  }'
```

Success — `202 Accepted`:

```json
{
  "payment_id": "cs_J1K2L3M4N5P6",
  "payment_link_id": "plink_A1B2C3D4E5F6",
  "merchant_reference": "ORDER-42",
  "payer_purpose": "Invoice 42",
  "amount": "50000.00",
  "currency": "TZS",
  "status": "processing",
  "failure_category": null,
  "created_at": "2026-08-12T10:02:00Z",
  "expires_at": "2026-08-12T10:17:00Z",
  "updated_at": "2026-08-12T10:02:00Z"
}
```

Save at least `payment_id`, `merchant_reference`, `status`, `amount`, and the
idempotency key in your own database.

### Callback URL rules

The callback override is optional and is not an unrestricted destination. It is
accepted only when:

- the Payment Link already has an active webhook configuration;
- the requested callback is a public HTTPS URL;
- its origin matches the registered link webhook origin; and
- DNS and network-safety checks pass.

If no override is supplied, events use the Payment Link's default webhook URL.
See [Webhooks](webhooks.md).

## Read payment status

```http
GET /api/integrations/v1/checkout-sessions/{sessionPublicId}
```

The `sessionPublicId` is the `payment_id` returned by payment creation.

Example:

```bash
curl https://app.payit.co.tz/api/integrations/v1/checkout-sessions/cs_J1K2L3M4N5P6 \
  -H 'X-PayIt-Api-Key: YOUR_API_KEY' \
  -H 'X-PayIt-Environment: test'
```

Success — `200 OK`:

```json
{
  "payment_id": "cs_J1K2L3M4N5P6",
  "payment_link_id": "plink_A1B2C3D4E5F6",
  "merchant_reference": "ORDER-42",
  "payer_purpose": "Invoice 42",
  "amount": "50000.00",
  "currency": "TZS",
  "status": "succeeded",
  "failure_category": null,
  "created_at": "2026-08-12T10:02:00Z",
  "expires_at": "2026-08-12T10:17:00Z",
  "updated_at": "2026-08-12T10:05:00Z"
}
```

## Payment statuses

| Status | Terminal? | Meaning | Merchant action |
|---|---:|---|---|
| `open` | No | Session exists but no provider attempt is active. | Normally wait or allow a valid attempt. |
| `processing` | No | Payment is queued, dispatched, or awaiting confirmation. | Continue polling; do not create a replacement payment. |
| `succeeded` | Yes | Payment and Pay-IT completion succeeded. | Fulfil the order exactly once. |
| `failed` | Yes for that session outcome | Payment failed. | Show failure and follow business retry policy. |
| `expired` | Yes | Session expired before successful completion. | Create a genuinely new payment with a new idempotency key if the customer retries. |
| `attempts_exhausted` | Yes | Maximum attempts were used. | Start a new payment only through an intentional customer action. |

Treat unknown future status values as non-terminal until your integration is
updated or the status endpoint confirms a documented terminal result.

## Polling recommendation

Webhooks should be the primary notification mechanism. Polling is the recovery
mechanism.

A simple policy is:

1. Poll after 2–3 seconds.
2. Poll every 3–5 seconds while the user is waiting.
3. Slow to every 15–30 seconds after the interactive window.
4. Stop frequent polling when the session is terminal or expired.
5. Reconcile older non-terminal payments periodically from your backend.

Respect `429` and use bounded backoff.

## Error response

Safe errors generally use this shape:

```json
{
  "ResponseCode": 403,
  "ResponseMessage": "The authenticated principal is not allowed to perform this action."
}
```

Common causes:

| HTTP | Likely cause |
|---:|---|
| `400` | Invalid amount, currency, mobile number, provider resolution, header, or callback URL. |
| `401` | API key is missing, malformed, revoked, or expired. |
| `403` | Wrong environment, missing scope, wrong merchant, or API initiation disabled. |
| `404` | Payment Link/payment is unavailable or belongs to another merchant. |
| `409` | Idempotency key was reused with different data or state conflicts. |
| `429` | Credential rate limit exceeded. |

## Minimal server-side example

```javascript
const idempotencyKey = `invoice-${invoice.id}-payment-${invoice.attempt}`;

const response = await fetch(
  "https://app.payit.co.tz/api/integrations/v1/mobile-money-payments",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-PayIt-Api-Key": process.env.PAYIT_API_KEY,
      "X-PayIt-Environment": process.env.PAYIT_ENVIRONMENT,
      "Idempotency-Key": idempotencyKey
    },
    body: JSON.stringify({
      payment_link_id: process.env.PAYIT_PAYMENT_LINK_ID,
      amount: invoice.amount.toFixed(2),
      currency: "TZS",
      mobile_number: customer.mobile,
      provider: "MPESA",
      merchant_reference: invoice.id,
      payer_purpose: `Invoice ${invoice.number}`
    })
  }
);

const result = await response.json();

if (response.status === 202) {
  await savePayment({
    paymentId: result.payment_id,
    idempotencyKey,
    status: result.status
  });
} else {
  throw new Error(result.ResponseMessage ?? "Pay-IT request was rejected");
}
```

## Go-live checklist

- Test successful, failed, delayed, and expired payments.
- Verify the same idempotency key cannot create two payments.
- Confirm your system does not fulfil on `202` or `processing`.
- Verify webhook signatures using the exact raw request body.
- Deduplicate webhook processing by event ID.
- Reconcile status when webhook delivery is delayed.
- Move the live API key into a production secrets manager.
- Use a live key with `X-PayIt-Environment: live`.
- Remove full phone numbers, API keys, and webhook secrets from logs.
