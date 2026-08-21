# Webhook integration guide

Webhooks are signed HTTP messages sent by Pay-IT to your server when a checkout
session changes. They let your system learn that a payment succeeded without
polling continuously.

This guide covers both sides:

- configuring and operating webhooks from the merchant dashboard; and
- receiving and verifying webhook messages in the merchant's backend.

## Webhook events

| Event | Meaning |
|---|---|
| `checkout.session.pending` | A payment attempt was accepted and is processing. |
| `checkout.session.succeeded` | Payment and Pay-IT completion succeeded. |
| `checkout.session.failed` | Checkout reached a terminal failure. |
| `checkout.session.expired` | Checkout expired before successful completion. |

Only `checkout.session.succeeded` should trigger order fulfilment. Process it
idempotently because the same event may be delivered more than once.

## Endpoint requirements

Your webhook URL must:

- use public HTTPS;
- use a DNS hostname, not a literal IP address;
- resolve only to public network addresses;
- contain no URL username or password;
- contain no query string or fragment;
- not use localhost, `.local`, private, loopback, or link-local networks;
- accept HTTP `POST` with `application/json`; and
- return a `2xx` response quickly after durably saving the event.

Pay-IT does not depend on redirects. Configure the final receiving URL.

**Include the receiver's full path.** A path is allowed and almost always
required. A bare origin such as `https://merchant.example` is accepted by
validation and delivers to `/`, where many web frameworks answer with a `200`
from an unrelated page handler. Delivery then looks successful while your
receiver never runs. Configure `https://merchant.example/payit/webhook`, not
`https://merchant.example`.

**Target safety is rechecked on every delivery attempt, not only when you
configure it.** The hostname must keep resolving to public addresses for the
life of the integration. A configuration that succeeded starts failing if DNS
changes, the host moves behind a private address, or a development tunnel is
recycled.

## Configure a webhook

This merchant-dashboard endpoint requires a merchant JWT and Payment Link
management permission.

There is no matching read endpoint. Unlike embed origins and redirects, webhook
configuration cannot be read back from the API. Record what you configured — the
webhook ID, host, subscribed events, and timeout — in your own system if you
need to display it later. The delivery list is the only indirect view of an
existing configuration.

```http
POST /api/Merchant/v2/payment-links/webhook/configure
Authorization: Bearer <merchant-jwt>
Content-Type: application/json
```

Request fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `MerchantId` | integer | Yes | Merchant owning the Payment Link. |
| `PaymentLinkId` | string | Yes | Public Payment Link ID. |
| `Version` | integer | Yes | Current link version for optimistic concurrency. |
| `Url` | string | Yes | Public HTTPS receiver URL. |
| `SubscribedEvents` | string array | Yes | One or more supported events. |
| `TimeoutSeconds` | integer | Yes | Delivery timeout from 1 to 30 seconds. |

Example:

```json
{
  "MerchantId": 7001,
  "PaymentLinkId": "plink_A1B2C3D4E5F6",
  "Version": 3,
  "Url": "https://merchant.example/payit/webhook",
  "SubscribedEvents": [
    "checkout.session.pending",
    "checkout.session.succeeded",
    "checkout.session.failed",
    "checkout.session.expired"
  ],
  "TimeoutSeconds": 10
}
```

Success — `200 OK`:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "WebhookId": "wh_A1B2C3D4E5F6",
  "Version": 4,
  "Host": "merchant.example",
  "Status": "ACTIVE",
  "SubscribedEvents": [
    "checkout.session.expired",
    "checkout.session.failed",
    "checkout.session.pending",
    "checkout.session.succeeded"
  ],
  "TimeoutSeconds": 10,
  "Secret": "whsec_DISPLAY_ONCE_SECRET"
}
```

`Secret` is returned only when a new webhook configuration creates the secret.
Store it immediately in a secrets manager. Updating an existing configuration
does not reveal its existing secret.

`SubscribedEvents` is returned sorted, not in the order you sent it. Duplicates
are collapsed, and `TimeoutSeconds` is clamped to 1–30.

### The link version changes on every save

A successful configure increments the Payment Link's version. `Version` in the
response is the value **after** the save.

Use it for the next versioned call on that link — `update`, `publish`,
`unpublish`, `archive`, `restore`, `embed-origins/configure`,
`redirects/configure`, or another `webhook/configure`. Reusing the version you
sent in the request will fail, because that value is now one behind.

This is the most common cause of a webhook configuration that saves once and
then refuses every later save from the same screen. If your interface holds a
version from page load, refresh it from the configure response or reload
`payment-links/details` before saving again.

### Configuration rejection causes

Each rejection has its own response code and HTTP status.

| HTTP | `ResponseCode` | Cause | Action |
|---:|---:|---|---|
| `409` | `1124` | `Version` does not match the stored link version. | Reload `payment-links/details` and retry with the returned `Version`. |
| `400` | `1125` | `Url` is not absolute HTTPS, or contains credentials, a query string, a fragment, an IP-literal host, loopback, `localhost`, or a `.local` host. | Correct the URL. |
| `400` | `1126` | The host did not resolve, or resolved to a private, loopback, link-local, CGNAT, or otherwise non-public address. | Use a publicly reachable host. |
| `400` | `1127` | `SubscribedEvents` is empty or contains an unsupported event name. | Send one or more supported events, matching case exactly. |
| `404` | `1101` | Payment Link not found for this merchant. | Check `PaymentLinkId` and `MerchantId`. |
| `403` | `901` | The session lacks Payment Link management permission. | Do not retry as the same user. |

Only `1124` is retryable, and only after reloading the current version. Branch
on `ResponseCode` rather than HTTP status alone; the code is the precise cause.

## Webhook HTTP request

Pay-IT sends:

```http
POST /payit/webhook HTTP/1.1
Content-Type: application/json; charset=utf-8
PayIT-Event-Id: evt_7YQ2M4N6P8R1
PayIT-Timestamp: 1786529100
PayIT-Signature: v1=lowercase_hex_signature
```

The body is similar to:

```json
{
  "id": "evt_7YQ2M4N6P8R1",
  "type": "checkout.session.succeeded",
  "api_version": "2026-08-03",
  "created_at": "2026-08-12T10:05:00Z",
  "data": {
    "payment_link_id": "plink_A1B2C3D4E5F6",
    "slug": "idea-school-fees",
    "payment_id": "cs_J1K2L3M4N5P6",
    "amount": "50000.00",
    "currency": "TZS",
    "merchant_reference": "ORDER-42",
    "payer_purpose": "Invoice 42",
    "payer_mode": "GUEST",
    "provider": "MPESA",
    "initiation_channel": "HOSTED_CHECKOUT",
    "status": "succeeded",
    "failure_category": null
  }
}
```

Webhook field reference:

| Field | Meaning |
|---|---|
| `id` | Stable event ID used for deduplication. |
| `type` | Event type from the supported event list. |
| `api_version` | Event contract version. |
| `created_at` | When Pay-IT created the event. |
| `data.payment_link_id` | Payment Link public ID. |
| `data.slug` | Human-readable Payment Link slug. |
| `data.payment_id` | Checkout/payment public ID. |
| `data.amount` | Decimal amount string. |
| `data.currency` | Payment currency, currently `TZS`. |
| `data.merchant_reference` | Merchant correlation reference, when supplied. |
| `data.payer_purpose` | Payer purpose, when supplied. |
| `data.payer_mode` | Common values are `GUEST` and `PAYIT_AUTHENTICATED`. |
| `data.provider` | Resolved MNO, when known. |
| `data.initiation_channel` | `HOSTED_CHECKOUT` or `MERCHANT_API`. |
| `data.status` | Canonical session state represented by the event. |
| `data.failure_category` | Safe failure category for failed events, otherwise `null`. |

## Verify the signature

Do not trust the JSON until the signature is verified.

Pay-IT calculates the signature as:

```text
signed_payload = PayIT-Timestamp + "." + exact_raw_request_body
signature = lowercase_hex(HMAC-SHA256(webhook_secret, signed_payload))
header = "v1=" + signature
```

Verification steps:

1. Read the **raw request bytes** before JSON parsing or reformatting.
2. Read `PayIT-Timestamp` and reject missing or invalid values.
3. Reject timestamps outside your configured replay-tolerance window. A common
   tolerance is five minutes.
4. Build `timestamp + "." + exactRawBody` using the header value exactly.
5. Calculate HMAC-SHA256 using the webhook secret.
6. Prefix the lowercase hexadecimal digest with `v1=`.
7. Compare the supplied and calculated signatures using a constant-time
   comparison.
8. Confirm `PayIT-Event-Id` equals the body `id`.
9. Deduplicate using the event ID.
10. Store the event durably, return `2xx`, and process business work separately.

Never parse and then reserialize JSON before verification; whitespace and
property formatting would change the signed bytes.

## Node.js verification example

This example assumes `rawBody` is the exact UTF-8 body captured before a JSON
body parser modifies it.

```javascript
import crypto from "node:crypto";

function verifyPayItWebhook({ rawBody, timestamp, signature, secret }) {
  const signedPayload = `${timestamp}.${rawBody}`;
  const expected = `v1=${crypto
    .createHmac("sha256", secret)
    .update(signedPayload, "utf8")
    .digest("hex")}`;

  const suppliedBuffer = Buffer.from(signature, "utf8");
  const expectedBuffer = Buffer.from(expected, "utf8");

  return suppliedBuffer.length === expectedBuffer.length &&
    crypto.timingSafeEqual(suppliedBuffer, expectedBuffer);
}
```

Receiver outline:

```javascript
app.post("/payit/webhook", rawJsonMiddleware, async (req, res) => {
  const rawBody = req.body.toString("utf8");
  const timestamp = req.header("PayIT-Timestamp");
  const signature = req.header("PayIT-Signature");
  const headerEventId = req.header("PayIT-Event-Id");

  if (!timestamp || !signature || !withinTolerance(timestamp)) {
    return res.sendStatus(401);
  }

  if (!verifyPayItWebhook({
    rawBody,
    timestamp,
    signature,
    secret: process.env.PAYIT_WEBHOOK_SECRET
  })) {
    return res.sendStatus(401);
  }

  const event = JSON.parse(rawBody);
  if (event.id !== headerEventId) return res.sendStatus(400);

  await saveEventIfNew(event.id, rawBody);
  res.sendStatus(204);
});
```

## Idempotent event processing

Your database should enforce uniqueness on `event.id`.

Recommended logic:

1. Start a database transaction.
2. Insert the event ID into a webhook-inbox table with a unique constraint.
3. If it already exists, return `2xx` without repeating business work.
4. Update the merchant order only if the new state is allowed.
5. Commit.

A successful payment state should be absorbing: a late pending or failure event
must not undo a successfully fulfilled payment.

## Delivery, retries, and ordering

Any HTTP status from `200` through `299` acknowledges the delivery. For a
non-2xx response, timeout, DNS problem, or transport failure, Pay-IT schedules a
retry.

The built-in retry schedule is approximately:

```text
initial, 30 seconds, 2 minutes, 10 minutes,
1 hour, 6 hours, 24 hours, 48 hours
```

A small deterministic jitter may move an attempt by a few seconds. The maximum
attempt count is runtime-configurable up to eight. Do not rely on exact delivery
time or event ordering.

Webhook delivery failure does not reverse or fail a payment. Status polling is
the backup source of truth.

## Test the webhook

The Payment Link must already have an `ACTIVE` webhook configuration and at
least one checkout session, because the test event uses the latest session as
safe context.

The failure message names only the session (`"Webhook test requires an existing
checkout session."`), but the same message is returned when no webhook is
configured, when the endpoint is not `ACTIVE`, and when the caller lacks
management permission. Check all of those before concluding that the session is
missing.

```http
POST /api/Merchant/v2/payment-links/webhook/test
Authorization: Bearer <merchant-jwt>
Content-Type: application/json
```

```json
{
  "MerchantId": 7001,
  "PaymentLinkId": "plink_A1B2C3D4E5F6"
}
```

Success queues a `webhook.test` delivery:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "Delivery": {
    "DeliveryId": "del_A1B2C3D4E5F6",
    "EventId": "evt_A1B2C3D4E5F6",
    "TargetSource": "LINK_DEFAULT",
    "TargetHost": "merchant.example",
    "Status": "QUEUED",
    "AttemptCount": 0,
    "NextAttemptAtUtc": "2026-08-12T10:00:00Z"
  }
}
```

## List deliveries

```http
POST /api/Merchant/v2/payment-links/webhook/deliveries
Authorization: Bearer <merchant-jwt>
Content-Type: application/json
```

Request:

```json
{
  "MerchantId": 7001,
  "PaymentLinkId": "plink_A1B2C3D4E5F6",
  "Status": "RETRY",
  "Page": 1,
  "PageSize": 20
}
```

`Status` is optional. Common values are `QUEUED`, `RETRY`, `SUCCEEDED`, and
`FAILED`.

Response:

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
      "DeliveryId": "del_A1B2C3D4E5F6",
      "EventId": "evt_A1B2C3D4E5F6",
      "TargetSource": "LINK_DEFAULT",
      "TargetHost": "merchant.example",
      "Status": "RETRY",
      "AttemptCount": 2,
      "NextAttemptAtUtc": "2026-08-12T10:12:00Z"
    }
  ]
}
```

## Manually replay a delivery

```http
POST /api/Merchant/v2/payment-links/webhook/replay
Authorization: Bearer <merchant-jwt>
Content-Type: application/json
```

```json
{
  "MerchantId": 7001,
  "PaymentLinkId": "plink_A1B2C3D4E5F6",
  "DeliveryId": "del_A1B2C3D4E5F6"
}
```

Replay creates a new delivery but preserves the original event ID. This is why
the receiver must deduplicate by event ID, not delivery count.

## Rotate the webhook secret

```http
POST /api/Merchant/v2/payment-links/webhook/rotate-secret
Authorization: Bearer <merchant-jwt>
Content-Type: application/json
```

```json
{
  "MerchantId": 7001,
  "PaymentLinkId": "plink_A1B2C3D4E5F6"
}
```

Success:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "WebhookId": "wh_A1B2C3D4E5F6",
  "Secret": "whsec_NEW_DISPLAY_ONCE_SECRET",
  "PreviousSecretValidUntilUtc": "2026-08-13T10:00:00Z"
}
```

During the overlap, verify against the new secret first and the previous secret
second.

**Do not use `PreviousSecretValidUntilUtc` as the moment it becomes safe to drop
the old secret.** That timestamp is 24 hours after the rotation and controls only
when Pay-IT purges its own stored copy. It does not stop deliveries signed with
the old secret from arriving.

Each delivery is signed with the secret held when the delivery was **queued**,
not when it is sent. A delivery queued moments before you rotate keeps being
signed with the old secret for its entire retry life, and the retry schedule
spans roughly 80 hours. A receiver that stops accepting the previous secret at
`PreviousSecretValidUntilUtc` will reject legitimate retries for up to two and a
half days after that timestamp.

Keep the previous secret accepted until pre-rotation deliveries can no longer
arrive — the full retry horizon, not the advisory window. You can confirm the
backlog has drained by checking the delivery list for `QUEUED` or `RETRY` rows
created before the rotation.

For the same reason, rotating a secret does not re-sign anything already queued.
If you are rotating because a secret leaked, treat every in-flight delivery as
signed by the compromised secret.

## Troubleshooting

| Problem | Check |
|---|---|
| Configuration rejected | Read `ResponseCode` — `1124` stale `Version`, `1125` malformed URL, `1126` non-public host, `1127` bad events, `1101` link not found, `901` no permission. |
| Saved once, every later save rejected | Stale `Version`. The link version increments on each save; re-read it from the configure response. |
| Deliveries appear successful but nothing is received | Webhook URL set to a bare origin, so deliveries reach `/` and an unrelated page handler answers `200`. Configure the receiver's full path. |
| Receiver never runs, host returns non-2xx | A receiver that rejects before verifying — for example when its signing secret is unset — discards every delivery. Confirm the secret is actually loaded in the running process, not merely present in a file. |
| Signature mismatch | Raw body captured before parsing, exact timestamp, correct current/previous secret, lowercase `v1=` format. |
| Signature mismatch only after a rotation | Deliveries queued before the rotation are still signed with the old secret. Keep accepting it until the pre-rotation backlog drains. |
| Repeated delivery | Return `2xx` only after durable receipt; deduplicate by event ID. |
| Delivery marked `RETRY` | Receiver HTTP status, timeout, TLS certificate, DNS, and public network accessibility. |
| Deliveries stopped after working | Target safety is rechecked every attempt. Confirm the host still resolves publicly; a recycled development tunnel is the usual cause. |
| Payment succeeded but no webhook | Check delivery list, then query payment status; webhook failure does not change payment state. |
| Test endpoint fails | Needs an `ACTIVE` webhook configuration, at least one checkout session, and management permission — the message names only the session. |
| Cannot read current webhook configuration | There is no read endpoint. Persist your own record of what you configured. |

