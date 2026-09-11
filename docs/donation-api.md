# Donation API

## Overview

Donations are **created automatically by the PayIt webhook** — the frontend does not create donations.

**Flow:**

1. PayIt creates a payment link for StreetLabs
2. User pays via that link
3. PayIt sends a webhook event → `POST /api/donations/webhook/`
4. Backend creates a `Donation` row + `DonationConfirmation` audit record
5. Backoffice can view, update, or delete donations

---

## Public Endpoints

### Donation Webhook

Receives PayIt webhook events. Each event creates a new `Donation` (or updates an existing one matched by `payment_id` / `payment_link_id`) and stores a `DonationConfirmation` for audit.

```
POST /api/donations/webhook/
Content-Type: application/json
```

**Request body** (array of events):

```json
[
  {
    "receivedAt": "2026-08-19T13:05:41.329Z",
    "eventId": "evt_826d4838510386b92d97d5ca4f9b2ccd",
    "eventType": "webhook.test",
    "timestamp": "1787144739",
    "duplicate": false,
    "payload": {
      "id": "evt_826d4838510386b92d97d5ca4f9b2ccd",
      "type": "webhook.test",
      "api_version": "2026-08-03",
      "created_at": "2026-08-19T13:05:38.895084Z",
      "data": {
        "slug": "deezman",
        "amount": "10000.00",
        "status": "test",
        "currency": "TZS",
        "payment_id": "cs_c8781f172f8d2b4914fd560f1a8a77a6",
        "payment_link_id": "plink_972c18ea4ccc288614a6ee56e7550e11",
        "initiation_channel": "HOSTED_CHECKOUT"
      }
    }
  }
]
```

**Response** `200 OK`

```json
{
  "processed": 1,
  "results": [
    {
      "event_id": "evt_826d4838510386b92d97d5ca4f9b2ccd",
      "donation_id": 1,
      "status": "pending",
      "confirmed": false
    }
  ]
}
```

**Webhook behavior:**

- Deduplicates by `eventId` — repeated events return `already recorded`
- Matches existing donations by `payment_id`, `external_reference`, `transaction_reference`, or `payment_link_id`
- Creates a new donation if no match found
- Sets `status` to `success` when `eventType` ends with `.success` or `data.status` is `success`
- Sets `status` to `failed` when `eventType` ends with `.failed` or `data.status` is `failed`
- Sets `confirmed: true` only on success events

---

## Backoffice Endpoints

All require JWT authentication:

```
Authorization: Bearer <access_token>
```

### List Donations

```
GET /api/donations/
```

**Query params:**

| Param           | Values                                           | Description                                                                 |
| --------------- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| `status`        | `pending`, `success`, `failed`                   | Filter by status                                                            |
| `confirmed`     | `true`, `false`                                  | Filter by confirmation state                                                |
| `currency`      | e.g. `TZS`, `USD`                                | Filter by currency                                                          |
| `donation_type` | `once`, `monthly`                                | Filter by type                                                              |
| `search`        | string                                           | Searches `donor_name`, `donor_email`, `transaction_reference`, `payment_id` |
| `ordering`      | `created_at`, `-created_at`, `amount`, `-amount` | Sort results                                                                |

**Response** `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "amount": "10000.00",
      "currency": "TZS",
      "donation_type": "once",
      "payment_method": 1,
      "payment_method_code": "mtn",
      "phone": "0712345678",
      "status": "success",
      "external_reference": "SLA-1787214915",
      "transaction_reference": "SLA-1787214915",
      "payment_id": "",
      "payment_link_id": "",
      "initiation_channel": "",
      "confirmed": false,
      "donor_name": "John Doe",
      "donor_email": "john@example.com",
      "created_at": "2026-08-20T11:35:08.497169+03:00",
      "updated_at": "2026-08-20T11:35:08.497190+03:00"
    }
  ]
}
```

### Retrieve Donation

```
GET /api/donations/{id}/
```

**Response** `200 OK` — single donation object (same fields as above)

### Update Donation

```
PATCH /api/donations/{id}/
Content-Type: application/json

{
  "status": "success",
  "confirmed": true,
  "donor_name": "Updated Name"
}
```

**Response** `200 OK` — updated donation object

### Delete Donation

```
DELETE /api/donations/{id}/
```

**Response** `204 No Content`

---

### List Donation Confirmations

```
GET /api/donation-confirmations/
```

**Query params:**

| Param        | Values                                                     | Description               |
| ------------ | ---------------------------------------------------------- | ------------------------- |
| `event_type` | e.g. `webhook.test`                                        | Filter by event type      |
| `duplicate`  | `true`, `false`                                            | Filter by duplicate flag  |
| `processed`  | `true`, `false`                                            | Filter by processed state |
| `donation`   | integer                                                    | Filter by donation ID     |
| `search`     | string                                                     | Searches `event_id`       |
| `ordering`   | `created_at`, `-created_at`, `received_at`, `-received_at` | Sort results              |

**Response** `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "event_id": "evt_826d4838510386b92d97d5ca4f9b2ccd",
      "event_type": "webhook.test",
      "received_at": "2026-08-19T16:05:41.329000+03:00",
      "timestamp": "1787144739",
      "duplicate": false,
      "payload": {
        "eventId": "evt_826d4838510386b92d97d5ca4f9b2ccd",
        "eventType": "webhook.test",
        "timestamp": "1787144739",
        "receivedAt": "2026-08-19T13:05:41.329Z",
        "duplicate": false,
        "payload": {
          "id": "evt_826d4838510386b92d97d5ca4f9b2ccd",
          "type": "webhook.test",
          "api_version": "2026-08-03",
          "created_at": "2026-08-19T13:05:38.895084Z",
          "data": {
            "slug": "deezman",
            "amount": "10000.00",
            "status": "test",
            "currency": "TZS",
            "payment_id": "cs_c8781f172f8d2b4914fd560f1a8a77a6",
            "payment_link_id": "plink_972c18ea4ccc288614a6ee56e7550e11",
            "initiation_channel": "HOSTED_CHECKOUT"
          }
        }
      },
      "donation": 1,
      "processed": true,
      "created_at": "2026-08-20T11:35:08.482846+03:00"
    }
  ]
}
```

### Retrieve Donation Confirmation

```
GET /api/donation-confirmations/{id}/
```

**Response** `200 OK` — single confirmation object

---

## Interactive Docs

- **Swagger UI**: `/api/docs/`
- **OpenAPI Schema**: `/api/schema/`
