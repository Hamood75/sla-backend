# Payment Links and Hosted Checkout Guide

This guide explains how a merchant creates a reusable payment link, publishes it, and accepts payments through PayIt's hosted checkout. Checkout can be shared as a normal page, opened in a modal, or embedded inline in a website. It is written for product teams and developers who need enough technical detail to integrate without needing to understand the PayIt backend.

For server-to-server payment initiation, see [Direct API integration](direct-api-integration.md). For payment notifications, see [Webhooks](webhooks.md).

## What a payment link does

A payment link defines:

- the public URL customers visit;
- the amounts customers may pay;
- the title and description displayed at checkout;
- whether customers may enter a payment purpose;
- whether the link may also be used through the direct API.

The usual lifecycle is:

```text
DRAFT -> PUBLISHED -> UNPUBLISHED
   |          |
   +----------+----> ARCHIVED -> DRAFT or UNPUBLISHED
```

An approved, active merchant with an active receiving account can publish its own link. There is no separate back-office approval for each link. Back office may still force-unpublish a link for operational or compliance reasons.

Only a `PUBLISHED` link is available at its public URL. Unpublished, archived, disabled, or otherwise unavailable links are intentionally returned as `404 Not Found`.

## Before you begin

You need:

- the API base URL, for example `https://app.payit.co.tz`;
- a merchant account that is approved and active;
- an active receiving payment account;
- a merchant JWT for the management endpoints.

Merchant management requests use `PascalCase`. Public hosted-checkout requests use `snake_case`.

## 1. Create a payment link

`POST /api/Merchant/v2/payment-links/create`

Authentication: `Authorization: Bearer <merchant-jwt>`

Example request:

```json
{
  "MerchantId": 42,
  "Slug": "school-fees",
  "Title": "School fees",
  "Description": "Pay term fees securely",
  "AmountMode": "PRESETS_AND_CUSTOM",
  "PresetAmounts": ["25000", "50000", "100000"],
  "MinimumCustomAmount": "1000",
  "MaximumCustomAmount": "500000",
  "Currency": "TZS",
  "StaticMerchantReference": "SCHOOL-2026",
  "AllowPayerPurpose": true,
  "AllowApiInitiation": true
}
```

### Configuration fields

| Field | Required | Description |
|---|---:|---|
| `MerchantId` | Yes | Merchant that owns the link. The authenticated user must be allowed to manage it. |
| `Slug` | Yes | Public URL name, 3–80 characters. Use lowercase letters, numbers, and internal hyphens, for example `school-fees`. It must be globally unique. |
| `Title` | Yes | Customer-facing title, up to 160 characters. |
| `Description` | No | Customer-facing explanation, up to 1,000 characters. |
| `AmountMode` | Yes | `PRESETS_ONLY`, `CUSTOM_ONLY`, or `PRESETS_AND_CUSTOM`. |
| `PresetAmounts` | Conditional | Positive TZS amounts, with at most two decimal places. The default maximum is six values. |
| `MinimumCustomAmount` | Conditional | Lower limit when custom amounts are enabled. |
| `MaximumCustomAmount` | Conditional | Upper limit when custom amounts are enabled. |
| `Currency` | Yes | Currently only `TZS`. |
| `StaticMerchantReference` | No | Default merchant reference, up to 120 characters. |
| `AllowPayerPurpose` | No | Allows the payer to add a purpose or note. |
| `AllowApiInitiation` | No | Allows this link to be used by the direct integration API. |

Amount rules:

- `PRESETS_ONLY` requires at least one preset and does not accept custom limits.
- `CUSTOM_ONLY` must not contain presets.
- `PRESETS_AND_CUSTOM` may contain both presets and custom limits.
- If both custom limits are supplied, the maximum must be greater than or equal to the minimum.

Example response:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "Status": "DRAFT",
  "Version": 1,
  "PublishedAtUtc": null,
  "CreatedAtUtc": "2026-08-12T10:00:00Z",
  "UpdatedAtUtc": "2026-08-12T10:00:00Z",
  "Link": {
    "Slug": "school-fees",
    "Title": "School fees",
    "Description": "Pay term fees securely",
    "AmountMode": "PRESETS_AND_CUSTOM",
    "PresetAmounts": ["25000", "50000", "100000"],
    "MinimumCustomAmount": "1000",
    "MaximumCustomAmount": "500000",
    "Currency": "TZS",
    "StaticMerchantReference": "SCHOOL-2026",
    "AllowPayerPurpose": true,
    "AllowApiInitiation": true
  }
}
```

Keep `PaymentLinkId` as the stable identifier. Your hosted-checkout frontend can place the slug in its customer-facing URL. It resolves that slug through `GET /api/public/payment-links/{slug}`, described below. The API host itself is `https://app.payit.co.tz`; the customer-facing page URL depends on your frontend deployment.

## 2. Manage payment links

All endpoints in this section require a merchant JWT and use JSON request bodies.

| Action | Endpoint | Important request fields |
|---|---|---|
| List links | `POST /api/Merchant/v2/payment-links/list` | `MerchantId`, optional `Status`, `Search`, `SortOrder`, `Page`, `PageSize` |
| Get details | `POST /api/Merchant/v2/payment-links/details` | `MerchantId`, `PaymentLinkId` |
| Update | `POST /api/Merchant/v2/payment-links/update` | All create fields plus `PaymentLinkId` and `Version` |
| Publish | `POST /api/Merchant/v2/payment-links/publish` | `MerchantId`, `PaymentLinkId`, `Version` |
| Unpublish | `POST /api/Merchant/v2/payment-links/unpublish` | `MerchantId`, `PaymentLinkId`, `Version` |
| Archive | `POST /api/Merchant/v2/payment-links/archive` | `MerchantId`, `PaymentLinkId`, `Version` |
| Restore | `POST /api/Merchant/v2/payment-links/restore` | `MerchantId`, `PaymentLinkId`, `Version` |

`Version` is an optimistic-lock value. Always send the latest value returned by the API. If another request changed the link first, reload it and ask the user to retry instead of silently overwriting the newer change.

After a link has been published once, its slug cannot be changed. This prevents previously shared URLs from unexpectedly pointing somewhere else.

### List response

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "Page": 1,
  "PageSize": 20,
  "TotalCount": 1,
  "TotalPages": 1,
  "Items": [
    {
      "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
      "Slug": "school-fees",
      "Title": "School fees",
      "Status": "PUBLISHED",
      "AmountMode": "PRESETS_AND_CUSTOM",
      "Currency": "TZS",
      "AllowApiInitiation": true,
      "PublishedAtUtc": "2026-08-12T10:05:00Z",
      "UpdatedAtUtc": "2026-08-12T10:05:00Z"
    }
  ]
}
```

## 3. Choose how customers open checkout

PayIt offers three ways to present the same published Payment Link:

| Experience | Best for | Integration |
|---|---|---|
| Standalone page | Links in messages, email, QR codes, or a full-page handoff | Send the customer to `https://payit.co.tz/pay/{slug}`. |
| Modal | A “Pay now” button that opens checkout over your page | Use the hosted JavaScript SDK with `mode: 'modal'`. This is the SDK default. |
| Inline | Checkout displayed inside part of your page | Use the hosted JavaScript SDK with `mode: 'inline'` and a container. |

Modal and inline checkout require your website's exact origin to be saved on the Payment Link. An origin is the scheme, host, and optional port—for example `https://shop.example.com`. It does not contain a path such as `/checkout`.

The internal embed URL is `https://payit.co.tz/embed/pay/{slug}`, but merchant applications should not construct it themselves. The SDK adds the authorized parent origin and one-time message-channel values, creates the restricted iframe, validates messages, and handles cleanup.

### Configure allowed website origins

First read the current configuration and `Version`:

`POST /api/Merchant/v2/payment-links/embed-origins/details`

Authentication: `Authorization: Bearer <merchant-jwt>`

```json
{
  "MerchantId": 42,
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11"
}
```

Example response:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "Version": 7,
  "EmbedEnabled": true,
  "AllowedOrigins": [
    "https://shop.example.com"
  ]
}
```

Replace the complete allowed-origin list with:

`POST /api/Merchant/v2/payment-links/embed-origins/configure`

```json
{
  "MerchantId": 42,
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "Version": 7,
  "AllowedOrigins": [
    "https://shop.example.com",
    "https://checkout.example.com:8443"
  ]
}
```

The response has the same shape as the details response and contains the new `Version`. The configure call replaces the whole list; it does not append one item. Send an empty list to disable embedding for that link without disabling its standalone checkout page.

Origin rules:

- production origins must use HTTPS;
- the origin must match the browser's `window.location.origin` exactly, including a non-default port;
- paths, query strings, fragments, wildcard hosts, IP addresses, and user information are rejected;
- the default limit is 10 origins per Payment Link;
- the API normalizes host casing, international domain names, and default ports;
- a stale `Version` returns a conflict—reload details before retrying.

### Configure standalone success and failure redirects

Redirect targets apply to the standalone `/pay/{slug}` page and SDK `redirect` mode. Embedded modal and inline checkout report UI events to the parent page instead of navigating the parent browser.

Read the current settings with:

`POST /api/Merchant/v2/payment-links/redirects/details`

The request contains `MerchantId` and `PaymentLinkId`, like the embed-origin details request.

Save settings with:

`POST /api/Merchant/v2/payment-links/redirects/configure`

```json
{
  "MerchantId": 42,
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "Version": 8,
  "SuccessRedirectUrl": "https://shop.example.com/payment/success",
  "FailureRedirectUrl": "https://shop.example.com/payment/failed",
  "RedirectDelaySeconds": 3
}
```

Example response:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "Version": 9,
  "SuccessRedirectUrl": "https://shop.example.com/payment/success",
  "FailureRedirectUrl": "https://shop.example.com/payment/failed",
  "RedirectDelaySeconds": 3
}
```

Use absolute HTTPS URLs in production. The delay must be from 0 through 10 seconds. Send `null` for either URL to clear it. On a terminal checkout, PayIt preserves your existing query parameters and adds `payit_payment_id` and `payit_status`. These browser values are convenient navigation context, not payment proof.

## 4. Add the hosted checkout JavaScript SDK

Load the SDK from the PayIt checkout origin. `defer` waits until the page has been parsed before running the script.

```html
<script src="https://payit.co.tz/sdk/checkout-v1.js" defer></script>
```

### Modal example

```html
<button id="pay-now" type="button">Pay now</button>

<script>
  window.addEventListener('DOMContentLoaded', function () {
    const checkout = window.PayIt.checkout({
      slug: 'school-fees',
      mode: 'modal',
      onReady: function () {
        console.log('Checkout is ready');
      },
      onProcessing: function (result) {
        console.log('Payment is processing', result.payment_id);
      },
      onSuccess: function (result) {
        // Update the screen, then wait for your verified webhook before fulfilment.
        console.log('Checkout reported success', result.payment_id);
      },
      onFailure: function (result) {
        console.log('Checkout ended without success', result.status);
      },
      onClose: function (result) {
        console.log('Checkout closed', result.reason);
      }
    });

    document.getElementById('pay-now').addEventListener('click', function () {
      checkout.open();
    });
  });
</script>
```

Open checkout after a customer action such as a button click. This avoids surprising navigation and works with normal browser interaction policies.

### Inline example

```html
<div id="payit-checkout"></div>

<script>
  window.addEventListener('DOMContentLoaded', function () {
    window.PayIt.checkout({
      slug: 'school-fees',
      mode: 'inline',
      container: '#payit-checkout',
      onSuccess: function (result) {
        console.log('Checkout reported success', result.payment_id);
      }
    }).open();
  });
</script>
```

`container` may be a CSS selector or a DOM element. The SDK adjusts the iframe height between 200 and 2,000 pixels as the hosted page changes.

### Redirect example

```js
const checkout = window.PayIt.checkout({
  slug: 'school-fees',
  mode: 'redirect'
});

checkout.open();
```

Redirect mode navigates to `https://payit.co.tz/pay/school-fees`. It does not use an iframe and does not provide completion callbacks; configure standalone success and failure redirects or use a signed webhook.

### SDK options

| Option | Required | Description |
|---|---:|---|
| `slug` | Yes | Published Payment Link slug, up to 80 characters. |
| `mode` | No | `modal` (default), `inline`, or `redirect`. |
| `container` | Inline only | CSS selector or DOM element that receives the iframe. |
| `onReady` | No | Called when embedded checkout initializes. |
| `onProcessing` | No | Called after a payment attempt enters processing. |
| `onSuccess` | No | Called once when embedded checkout reports `SUCCEEDED`. |
| `onFailure` | No | Called once for `ATTEMPTS_EXHAUSTED`, `EXPIRED`, or `CANCELLED`. |
| `onClose` | No | Called when the iframe or merchant code closes checkout. |

`onProcessing`, `onSuccess`, and `onFailure` receive `{ payment_id, status }`. `onClose` receives a `reason`, currently `merchant_close`, `iframe_close`, or `destroyed`.

The returned checkout instance provides:

| Method | Purpose |
|---|---|
| `open()` | Opens the modal/inline checkout or starts redirect navigation. Repeated calls while open do nothing. |
| `close()` | Closes an open embedded checkout and reports `merchant_close`. |
| `destroy()` | Removes the embedded checkout and reports `destroyed`. |
| `isOpen()` | Returns whether modal or inline checkout is currently open. |

### Security and fulfillment rules

- Configure the exact origin on every Payment Link used in modal or inline mode.
- Keep the full-page `/pay/{slug}` URL outside third-party iframes; PayIt intentionally blocks framing of that route. Use the SDK and dedicated embed route instead.
- Do not listen for raw `window.postMessage` events. The SDK validates the PayIt origin, iframe window, protocol version, instance ID, nonce, and allowed event names.
- Treat SDK callbacks and redirect query parameters as user-interface signals only. Fulfil an order only after a verified signed webhook or an authenticated server-side status check.
- Do not place merchant JWTs, integration API keys, webhook secrets, checkout tokens, or payer details in the SDK options.
- If the configured origin is missing, embedding is disabled globally, the link is unavailable, or authorization times out, the embed fails closed as an indistinguishable `404`.

> **Rollout note:** the SDK and embed route must be deployed, the Payment Link embed database migration must be applied, and PayIt operations must enable `payment_links_embed_enabled` before modal or inline checkout can load in an environment.

## 5. Low-level hosted checkout API

Most merchant websites should use the hosted SDK above. Use the endpoints in the following sections only when you are building or diagnosing a custom checkout flow and accept responsibility for protecting the display-once checkout credentials.

### 5.1 Resolve a public link

`GET /api/public/payment-links/{slug}`

Authentication: none

Example response:

```json
{
  "payment_link_id": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "slug": "school-fees",
  "title": "School fees",
  "description": "Pay term fees securely",
  "amount_mode": "PRESETS_AND_CUSTOM",
  "preset_amounts": ["25000", "50000", "100000"],
  "minimum_custom_amount": "1000",
  "maximum_custom_amount": "500000",
  "currency": "TZS",
  "merchant_reference": "SCHOOL-2026",
  "allow_payer_purpose": true
}
```

Use this response to render the checkout form. Do not hard-code amount rules in the frontend; validate against the values returned by the API.

### 5.2 Create a checkout session

`POST /api/public/payment-links/{slug}/checkout-sessions`

Authentication: none

Required header:

```http
Idempotency-Key: checkout-order-88421
Content-Type: application/json
```

Use a unique and stable idempotency key for one intended checkout creation. Retrying the same operation with the same key prevents accidental duplicate sessions.

Example request:

```json
{
  "amount": "50000",
  "currency": "TZS",
  "payer_purpose": "Term 2 fees for Asha",
  "merchant_reference": "STUDENT-88421"
}
```

`payer_purpose` is accepted only when the link allows it. A non-empty caller-supplied `merchant_reference` overrides the link's static reference for this checkout; when omitted, the configured static reference is used.

Successful response: `201 Created`

```json
{
  "payment_id": "pay_24d8e6a0f99a4bd4",
  "payment_link_id": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "amount": "50000",
  "currency": "TZS",
  "status": "open",
  "checkout_token": "checkout-secret-returned-once",
  "checkout_challenge": "challenge-returned-once",
  "encrypted_transaction_id": "encrypted-transaction-reference",
  "created_at": "2026-08-12T10:10:00Z",
  "expires_at": "2026-08-12T10:25:00Z"
}
```

Store these values only for the lifetime of the checkout:

- `checkout_token` authorizes guest payment submission and public status reads. Send it as `Authorization: Checkout <token>`.
- `checkout_challenge` authorizes the one-time handoff into a logged-in PayIt account. It can be consumed only once and is not a login credential.
- `encrypted_transaction_id` binds the logged-in authorization and status request to this transaction.

The API stores digests rather than reusable plaintext copies of the token and challenge. If the browser loses them, create a new checkout session instead of attempting to recover them.

### 5.3 Guest mobile-money checkout

Use this flow when the payer does not log in to PayIt.

`POST /api/public/checkout-sessions/{sessionPublicId}/mobile-money-attempts`

Headers:

```http
Authorization: Checkout checkout-secret-returned-once
Content-Type: application/json
```

Request:

```json
{
  "mobile_number": "255712345678",
  "provider": "MPESA"
}
```

The `provider` field is currently required for contract compatibility, but routing derives the mobile network from the normalized phone number. Do not use the field to force a different network.

Successful response: `202 Accepted`

```json
{
  "attempt_id": "pattempt_c8ec10e9c1f44a3a",
  "payment_id": "pay_24d8e6a0f99a4bd4",
  "status": "processing",
  "created_at": "2026-08-12T10:11:00Z"
}
```

Payment execution is asynchronous. Guest hosted-checkout attempts route directly through Selcom. A `202` response means the attempt was accepted for processing, not that money was collected.

### Read guest checkout status

`GET /api/public/checkout-sessions/{sessionPublicId}`

Header:

```http
Authorization: Checkout checkout-secret-returned-once
```

Example response:

```json
{
  "payment_id": "pay_24d8e6a0f99a4bd4",
  "payment_link_id": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "merchant_reference": "STUDENT-88421",
  "payer_purpose": "Term 2 fees for Asha",
  "amount": "50000",
  "currency": "TZS",
  "status": "processing",
  "attempt_count": 1,
  "failure_category": null,
  "expires_at": "2026-08-12T10:25:00Z",
  "updated_at": "2026-08-12T10:11:01Z"
}
```

An invalid payment ID or checkout token is deliberately reported as `404`, so the endpoint does not reveal whether a session exists.

### 5.4 “I have a PayIt account” checkout

Use this flow when the payer logs in and chooses one of their saved payment accounts.

1. Create the public checkout session as described above.
2. Authenticate the customer normally and obtain a customer JWT.
3. Show the customer's active saved mobile-money accounts.
4. Submit the selected account with the one-time checkout challenge.

`POST /api/Customer/CheckoutPayments/Authorize`

Authentication: `Authorization: Bearer <customer-jwt>`

Request:

```json
{
  "SessionPublicId": "pay_24d8e6a0f99a4bd4",
  "EncryptedTransactionId": "encrypted-transaction-reference",
  "CheckoutChallenge": "challenge-returned-once",
  "PaymentAccountId": 781
}
```

The selected account must be active, owned by the authenticated customer, and be a supported mobile-money account. PayIt uses the saved account's provider and number; the customer does not re-enter the number.

Example accepted response:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "SessionPublicId": "pay_24d8e6a0f99a4bd4",
  "EncryptedTransactionId": "encrypted-transaction-reference",
  "Status": "processing",
  "Amount": "50000",
  "Currency": "TZS",
  "FailureCategory": null
}
```

The challenge is consumed when authorization succeeds and cannot be replayed. Payment processing remains asynchronous.

Authenticated checkout uses the same saved-account routing policy as the normal Make Payment flow: M-Pesa may use PayIt as its primary route, while Mixx and other supported networks route directly to Selcom. The system does not fall through to another gateway after an ambiguous response because that could create a duplicate debit.

### Read logged-in checkout status

`GET /api/Customer/CheckoutPayments/Status?SessionPublicId={payment_id}&EncryptedTransactionId={value}`

Authentication: `Authorization: Bearer <customer-jwt>`

The response uses the same `CustomerCheckoutStatusResponse` shape shown above. The authenticated customer must own the checkout attempt.

### 5.5 Checkout statuses

A checkout session has exactly six states.

| Status | Terminal | Meaning | UI guidance |
|---|:---:|---|---|
| `open` | No | Session exists but no attempt has been submitted. | Show payment options. |
| `processing` | No | An attempt is queued, dispatched, or awaiting a provider result. | Show a waiting state and poll gently. |
| `succeeded` | Yes | Payment completed successfully. | Show confirmation and stop polling. |
| `attempts_exhausted` | Yes | Every permitted attempt failed. This is the terminal failure state. | Show failure; a new session is required to try again. |
| `expired` | Yes | The session timed out before completion. | Create a new session. |
| `cancelled` | Yes | The session was cancelled. | Show a cancelled state. |

There is no `failed` session status. A payment that fails terminally leaves the session in `attempts_exhausted`; the individual attempts inside it carry their own statuses. Read `failure_category` for the safe reason.

### Status casing differs by surface

The same value is returned in different case depending on which API returned it. Compare case-insensitively rather than hardcoding one form.

| Surface | Casing | Example |
|---|---|---|
| Public checkout (`/api/public/...`) | lowercase | `"status": "processing"` |
| Merchant integration API (`/api/integrations/v1/...`) | lowercase | `"status": "processing"` |
| Logged-in customer checkout (`/api/Customer/CheckoutPayments/...`) | lowercase | `"Status": "processing"` |
| Webhook `data.status` | lowercase | `"status": "succeeded"` |
| Merchant dashboard checkout-session list | UPPERCASE | `"Status": "SUCCEEDED"` |
| Hosted checkout SDK callback payloads | UPPERCASE | `{ payment_id, status: "SUCCEEDED" }` |

The SDK callback values are produced by the hosted checkout page, not by the status API, which is why they are uppercase while the API surfaces they mirror are lowercase. The callback set is `PROCESSING`, `SUCCEEDED`, `ATTEMPTS_EXHAUSTED`, `EXPIRED`, and `CANCELLED`.

Payment Link lifecycle statuses are unrelated to these and are always uppercase: `DRAFT`, `PUBLISHED`, `UNPUBLISHED`, `ARCHIVED`.

Treat the API's returned status as authoritative. Do not infer success from a mobile-money prompt or from the initial `202` response.

## Analytics and checkout history

### Summary analytics

`POST /api/Merchant/v2/payment-links/analytics/summary`

```json
{
  "MerchantId": 42,
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "FromDate": "2026-08-01",
  "ToDate": "2026-08-31"
}
```

Example response:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "PageViewCount": 310,
  "SessionCount": 125,
  "SuccessfulCount": 98,
  "FailedCount": 17,
  "ExpiredCount": 10,
  "GrossSuccessfulAmount": "4900000",
  "ConversionRate": 78.4
}
```

### Checkout-session list

`POST /api/Merchant/v2/payment-links/checkout-sessions/list`

```json
{
  "MerchantId": 42,
  "PaymentLinkId": "plink_972c18ea4ccc288614a6ee56e7550e11",
  "Status": "SUCCEEDED",
  "InitiationChannel": "HOSTED",
  "FromDate": "2026-08-01",
  "ToDate": "2026-08-31",
  "SortOrder": "desc",
  "Page": 1,
  "PageSize": 20
}
```

Each item contains `SessionPublicId`, `Status`, `InitiationChannel`, `MerchantReference`, `Amount`, `Currency`, `AttemptCount`, `ExpiresAtUtc`, and `UpdatedAtUtc`.

## Errors and safe handling

Public endpoints use a compact error body:

```json
{
  "error": "The checkout session could not be processed."
}
```

Merchant endpoints use the standard response envelope with `ResponseCode` and `ResponseMessage`.

Common cases:

| HTTP status | Typical cause | What to do |
|---:|---|---|
| `400` | Invalid amount, currency, slug, state transition, or request field. | Correct the request; do not retry unchanged. |
| `401` | Missing or invalid JWT/checkout token. | Re-authenticate or restart checkout. |
| `403` | User cannot manage the merchant or selected account. | Do not retry as the same user. |
| `404` | Link/session unavailable, or checkout token does not match. | Show unavailable/expired and avoid exposing internal detail. |
| `409` | Version or idempotency conflict. | Reload current state or use the correct idempotency key. |
| `429` | Public API rate limit reached. | Back off before retrying. |
| `500`/`503` | Temporary service problem. | Retry safely using the same idempotency key. |

Merchant Payment Link endpoints currently return `400` for most conflict and not-found conditions, including a stale `Version`, rather than the `409` or `404` the condition implies. `webhook/configure` is the exception and returns accurate statuses. Until the remaining endpoints are aligned, branch on `ResponseCode` and `ResponseMessage` rather than on HTTP status alone.

## Go-live checklist

- Create the link and verify all amount rules.
- Configure and verify webhooks before publishing.
- Publish the link and test its public resolution.
- Test guest checkout with a real supported mobile number.
- If offered, test the logged-in saved-account flow.
- Confirm your UI handles `processing` without declaring success early.
- Confirm the `succeeded`, `attempts_exhausted`, `expired`, and `cancelled` terminal states, and that status comparison is case-insensitive.
- Confirm duplicate clicks reuse the same idempotency key.
- Confirm secrets and checkout tokens are not written to browser analytics or application logs.
- Reconcile using `payment_id` and your `merchant_reference`.

## Related guides

- [API credentials](api-credentials.md)
- [Direct API integration](direct-api-integration.md)
- [Webhooks](webhooks.md)

The canonical machine-readable contract remains [`Backend/api/core-engine/api-docs/spec.yaml`](../Backend/api/core-engine/api-docs/spec.yaml).
