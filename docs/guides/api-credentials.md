# API credentials guide

This guide explains how an authorized merchant user creates and manages the API
keys used by a merchant's backend integration.

## Key concepts

- API keys belong to an existing merchant account. There is no separate
  developer identity.
- Key-management endpoints are called from the authenticated merchant dashboard
  using a merchant JWT.
- The generated integration key is used only by a trusted backend against
  `/api/integrations/v1/*`.
- A full key is displayed once after creation or rotation. Pay-IT cannot show it
  again later.

## Environments

| Environment | Key prefix | Use |
|---|---|---|
| `test` | `mk_test_` | Testing and integration validation |
| `live` | `mk_live_` | Real production payments |

An integration request must send the same environment in
`X-PayIt-Environment`. A test key cannot be used as a live key.

## Available scopes

| Scope | Permission |
|---|---|
| `payment_links:read` | Read an integration-safe Payment Link. |
| `checkout_sessions:read` | Read the status of an API-created payment. |
| `mobile_money_payments:create` | Create a mobile-money payment. |

Use the minimum scopes your integration needs. Scope names are case-sensitive.

## Management authentication

All endpoints in this guide require:

```http
Authorization: Bearer <merchant-jwt>
Content-Type: application/json
```

The authenticated merchant user must be the merchant's operational account or
have active permission to manage Payment Links. Every request is also scoped by
`MerchantId`.

Base path:

```text
/api/Merchant/v2/integrations/api-keys
```

## Create an API key

```http
POST /api/Merchant/v2/integrations/api-keys/create
```

Request fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `MerchantId` | integer | Yes | Merchant receiving payments. |
| `Environment` | string | Yes | `test` or `live`. |
| `Scopes` | string array | Yes | At least one supported scope. |
| `ExpiresAtUtc` | UTC datetime or `null` | No | Optional future expiry. |

Example:

```bash
curl -X POST https://app.payit.co.tz/api/Merchant/v2/integrations/api-keys/create \
  -H 'Authorization: Bearer MERCHANT_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "MerchantId": 7001,
    "Environment": "test",
    "Scopes": [
      "payment_links:read",
      "checkout_sessions:read",
      "mobile_money_payments:create"
    ],
    "ExpiresAtUtc": "2027-08-12T12:00:00Z"
  }'
```

Success — `200 OK`:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "Metadata": {
    "ApiKeyId": "mkid_A1B2C3D4E5F6G7H8",
    "Prefix": "mk_test_A1B2C3D4E5F6G7H8",
    "Environment": "test",
    "Scopes": [
      "checkout_sessions:read",
      "mobile_money_payments:create",
      "payment_links:read"
    ],
    "Status": "ACTIVE",
    "ExpiresAtUtc": "2027-08-12T12:00:00Z",
    "LastUsedAtUtc": null
  },
  "ApiKey": "mk_test_A1B2C3D4E5F6G7H8_DISPLAY_ONCE_SECRET",
  "CreatedAtUtc": "2026-08-12T12:00:00Z"
}
```

Immediately copy `ApiKey` into a secure secrets manager. Do not store it in the
frontend or rely on being able to retrieve it again.

## List API keys

```http
POST /api/Merchant/v2/integrations/api-keys/list
```

Request fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `MerchantId` | integer | Yes | Merchant whose keys will be listed. |
| `Environment` | string or `null` | No | Filter by `test` or `live`. |
| `Status` | string or `null` | No | Common values are `ACTIVE` and `REVOKED`. |
| `Page` | integer | No | Defaults to page 1. |
| `PageSize` | integer | No | Between 1 and 100; default 20. |

Example request:

```json
{
  "MerchantId": 7001,
  "Environment": "test",
  "Status": "ACTIVE",
  "Page": 1,
  "PageSize": 20
}
```

Success — `200 OK`:

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
      "ApiKeyId": "mkid_A1B2C3D4E5F6G7H8",
      "Prefix": "mk_test_A1B2C3D4E5F6G7H8",
      "Environment": "test",
      "Scopes": ["payment_links:read", "checkout_sessions:read"],
      "Status": "ACTIVE",
      "ExpiresAtUtc": "2027-08-12T12:00:00Z",
      "LastUsedAtUtc": "2026-08-12T12:30:00Z"
    }
  ]
}
```

The secret is never included in list responses.

## Rotate an API key

Rotation creates replacement secret material. The environment stays the same.
Send the complete desired scope list because omitted scopes are not implicitly
copied.

```http
POST /api/Merchant/v2/integrations/api-keys/rotate
```

Request:

```json
{
  "MerchantId": 7001,
  "ApiKeyId": "mkid_A1B2C3D4E5F6G7H8",
  "Scopes": [
    "payment_links:read",
    "checkout_sessions:read",
    "mobile_money_payments:create"
  ],
  "ExpiresAtUtc": "2027-08-12T12:00:00Z"
}
```

The response has the same shape as key creation and includes the replacement
`ApiKey` once. Deploy the replacement securely, verify it, and retire the old
credential according to the rotation response and merchant policy.

## Revoke an API key

```http
POST /api/Merchant/v2/integrations/api-keys/revoke
```

Request:

```json
{
  "MerchantId": 7001,
  "ApiKeyId": "mkid_A1B2C3D4E5F6G7H8"
}
```

Success — `200 OK`:

```json
{
  "ResponseCode": 0,
  "ResponseMessage": "Success",
  "ApiKey": {
    "ApiKeyId": "mkid_A1B2C3D4E5F6G7H8",
    "Prefix": "mk_test_A1B2C3D4E5F6G7H8",
    "Environment": "test",
    "Scopes": ["payment_links:read", "checkout_sessions:read"],
    "Status": "REVOKED",
    "ExpiresAtUtc": "2027-08-12T12:00:00Z",
    "LastUsedAtUtc": "2026-08-12T12:30:00Z"
  }
}
```

Revocation is immediate. Any integration still using the key will begin
receiving authentication errors.

## Using the key

Send the full display-once key from a trusted backend:

```http
X-PayIt-Api-Key: mk_test_A1B2C3D4E5F6G7H8_DISPLAY_ONCE_SECRET
X-PayIt-Environment: test
```

Do not use `Authorization: Bearer` for direct integration endpoints.

## Operational checklist

- Keep separate test and live keys.
- Give each integration its own key so it can be revoked independently.
- Store full keys only in a secrets manager or protected environment variable.
- Display only the safe prefix in dashboards and support tickets.
- Rotate credentials periodically and immediately after suspected exposure.
- Revoke unused credentials.
- Review `LastUsedAtUtc` for unexpected or abandoned keys.
- Never log the value of `X-PayIt-Api-Key`.

