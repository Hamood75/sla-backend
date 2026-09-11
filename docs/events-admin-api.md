# Events Admin API Guide

All admin endpoints require `Authorization: Bearer <JWT>` header.  
JWT is obtained via `POST /api/auth/login/` with `{"username": "...", "password": "..."}`.

Roles allowed: `SUPER_ADMIN`, `ADMIN`, `EDITOR` (or `is_superuser`).

All admin endpoints return **snake_case** field names. Upload form fields and media library query params use **camelCase** (`altText`, `eventId`, `fileBase64`).

Image and file fields use Django `ImageField`/`FileField` — responses return **absolute URLs** (e.g. `"http://localhost:8089/media/events/villages/govtech.png"`). On create/update, these fields accept **base64 data URIs** (`data:image/png;base64,...`) in JSON or **multipart file uploads**. This applies to all image/file fields across all endpoints (`image`, `logo`, `photo`, `hero_image`, `file_base64`, etc.).

## Table of Contents

1. [Expo Events](#1-expo-events) — list, retrieve (with all nested sub-items), create, update, delete, activate, publish, unpublish, list years/editions, manage hero images
2. [Event Stats](#2-event-stats) — CRUD
3. [Focus Areas](#3-focus-areas) — CRUD
4. [Partners](#4-partners) — CRUD with tier filter
5. [Villages](#5-villages) — list, create, retrieve (with nested booths/schedule/gallery), update, delete
6. [Village Booths](#6-village-booths) — CRUD
7. [Village Schedules](#7-village-schedules) — CRUD
8. [Village Galleries](#8-village-galleries) — CRUD
9. [Booth Applications](#9-booth-applications) — list, retrieve, status update, delete
10. [Registrations](#10-registrations) — list, retrieve, update, delete
11. [Speakers](#11-speakers) — CRUD
12. [Sessions](#12-sessions) — CRUD with nested speaker
13. [Media Assets](#13-media-assets) — upload, list, update, delete, media library browser
14. [Dashboard Metrics](#14-dashboard-metrics) — aggregated stats
15. [Badge Export](#15-badge-export-csv) — CSV download
16. [Event Hero Images](#16-event-hero-images) — CRUD
17. [Village Highlights](#17-village-highlights) — CRUD

---

## 1. Expo Events

### 1.1 List Events

`GET /api/admin/expo-events/`

**Query params:** None (paginated by DRF default)

**Response `200`**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "year": 2026,
      "title": "Tanzania DPI Expo 2026",
      "tagline": "Building Digital Foundation",
      "description": "...",
      "start_date": "2026-11-18T11:00:00+03:00",
      "end_date": "2026-11-19T21:00:00+03:00",
      "venue_name": "Diamond Jubilee Expo Center",
      "venue_address": "Ohio Street, Dar es Salaam",
      "venue_lat": -6.8161,
      "venue_lng": 39.2804,
      "hero_images": [
        {
          "id": "uuid",
          "image": "http://localhost:8089/media/events/heroes/hero_1.jpg",
          "order": 1,
          "created_at": "...",
          "updated_at": "..."
        }
      ],
      "is_active": true,
      "is_published": true,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

### 1.2 Retrieve Event (with nested data)

`GET /api/admin/expo-events/{year}/`

Returns full event with nested `stats`, `focus_areas`, `partners`, `villages`, `speakers`, `sessions`, `booth_applications`, and `registrations` — everything the admin needs to manage an event in one request.

**Response `200`**

```json
{
  "id": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
  "year": 2026,
  "title": "Tanzania DPI Expo 2026",
  "tagline": "Building Digital Foundation",
  "description": "Test event",
  "start_date": "2026-11-18T11:00:00+03:00",
  "end_date": "2026-11-19T21:00:00+03:00",
  "venue_name": "Diamond Jubilee",
  "venue_address": "Ohio Street",
  "venue_lat": -6.8161,
  "venue_lng": 39.2804,
  "hero_images": [
    {
      "id": "uuid",
      "image": "http://localhost:8089/media/events/heroes/hero_1.jpg",
      "order": 1,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "is_active": true,
  "is_published": true,
  "created_at": "2026-08-28T17:35:39.681724+03:00",
  "updated_at": "2026-08-28T17:36:21.994815+03:00",
  "stats": [
    {
      "id": "16b18176-dfb4-4e5f-9ad3-9c48ea7a5062",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "label": "Speakers",
      "value": "50+",
      "order": 1,
      "created_at": "2026-08-28T17:36:00.000000+03:00",
      "updated_at": "2026-08-28T17:36:00.000000+03:00"
    }
  ],
  "focus_areas": [
    {
      "id": "d00919bd-98d3-4d4c-9896-3a0066f78215",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "num": "01",
      "title": "Keynotes",
      "description": "Inspiring talks",
      "accent_color": "#F97316",
      "badge_color": "#EA580C",
      "image": "http://localhost:8089/media/events/focus-areas/focus_01.png",
      "order": 1,
      "created_at": "2026-08-28T17:36:00.000000+03:00",
      "updated_at": "2026-08-28T17:36:00.000000+03:00"
    }
  ],
  "partners": [
    {
      "id": "ff68812c-0cda-442e-a430-02f3bb5adb17",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "name": "iDEA",
      "logo": "http://localhost:8089/media/events/logos/idea.png",
      "tier": "HOST",
      "website_url": "",
      "order": 1,
      "created_at": "2026-08-28T17:36:00.000000+03:00",
      "updated_at": "2026-08-28T17:36:00.000000+03:00"
    }
  ],
  "villages": [
    {
      "id": "8ee10f8f-0cb5-4a52-9a63-77ba0ffd63b1",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "slug": "govtech",
      "name": "GovTech Village",
      "hall": "Hall A",
      "emoji": "🏛️",
      "theme_color": "#2563EB",
      "tagline": "Transforming Public Services",
      "description": "Live demos of e-Government platforms...",
      "hero_image": "http://localhost:8089/media/events/villages/govtech.png",
      "booths_count": 14,
      "demos_count": 8,
      "order": 1
    }
  ],
  "speakers": [
    {
      "id": "11c093c0-f842-4355-990c-a13742d79549",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "name": "Dr. Fatma Hassan",
      "title": "Minister of ICT",
      "org": "Government of Tanzania",
      "initials": "FH",
      "color": "#1E40AF",
      "accent_light": "#DBEAFE",
      "photo": "http://localhost:8089/media/events/speakers/FH.png",
      "bio": "Leading national telecommunication transformation.",
      "order": 1,
      "is_confirmed": true,
      "is_approved": true
    }
  ],
  "sessions": [
    {
      "id": "uuid",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "day_number": 1,
      "start_time": "09:00",
      "end_time": "10:00",
      "title": "Opening Keynote",
      "type": "KEYNOTE",
      "speaker": { "id": "uuid", "name": "Dr. Fatma Hassan", ... },
      "speaker_id": "uuid",
      "speaker_text": "",
      "location": "Main Hall",
      "order": 1
    }
  ],
  "booth_applications": [
    {
      "id": "uuid",
      "reference_no": "TZ-DPI-BOOTH-0BAD1DFA",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "village": "uuid",
      "company_name": "Tech Co",
      "company_website": "https://...",
      "company_sector": "Fintech",
      "booth_package": "STANDARD",
      "showcase_title": "AI Demo",
      "showcase_desc": "AI powered solutions",
      "tech_requirements": ["..."],
      "co_exhibitors": "",
      "first_name": "Alice",
      "last_name": "Kimaro",
      "email": "alice@techco.com",
      "phone": "+255...",
      "job_title": "Head of Partnerships",
      "country": "Tanzania",
      "status": "PENDING_REVIEW",
      "assigned_booth_no": "",
      "admin_notes": "",
      "agree_terms": true,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "registrations": [
    {
      "id": "uuid",
      "reference_no": "TZ-DPI-GUE-BB20C79C",
      "event": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7",
      "type": "GUEST",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+255123456789",
      "country": "Tanzania",
      "organization": "Test Org",
      "extra_data": { "guest_category": "", "dietary_reqs": "" },
      "status": "CONFIRMED",
      "badge_code": "QR-TZ-DPI-GUE-BB20C79C",
      "agree_terms": true,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

### 1.3 Create Event

`POST /api/admin/expo-events/`

**Request body**

```json
{
  "year": 2028,
  "title": "Tanzania DPI Expo 2028",
  "tagline": "...",
  "description": "...",
  "start_date": "2028-11-18T08:00:00Z",
  "end_date": "2028-11-19T18:00:00Z",
  "venue_name": "...",
  "venue_address": "...",
  "venue_lat": -6.8161,
  "venue_lng": 39.2804,
  "hero_images": ["https://..."],
  "is_active": false,
  "is_published": false
}
```

**Response `201`** — same shape as list item.

### 1.4 Update Event

`PATCH /api/admin/expo-events/{year}/` — partial update.  
`PUT /api/admin/expo-events/{year}/` — full update.

### 1.5 Delete Event

`DELETE /api/admin/expo-events/{year}/` — `204 No Content`

### 1.6 Activate Event

`PATCH /api/admin/expo-events/{year}/activate/`

Deactivates all other events, activates this one.

**Response `200`**

```json
{
  "success": true,
  "message": "Event 2026 activated.",
  "data": { "id": "uuid", "year": 2026, "is_active": true, ... }
}
```

### 1.7 Publish Event

`PATCH /api/admin/expo-events/{year}/publish/`

**Response `200`**

```json
{
  "success": true,
  "message": "Event 2026 published.",
  "data": { "id": "uuid", "year": 2026, "is_published": true, ... }
}
```

### 1.8 Unpublish Event

`PATCH /api/admin/expo-events/{year}/unpublish/`

**Response `200`**

```json
{
  "success": true,
  "message": "Event 2026 unpublished.",
  "data": { "id": "uuid", "year": 2026, "is_published": false, ... }
}
```

### 1.8 List Years / Editions

`GET /api/admin/expo-events/years/`

Returns all event editions/years ordered by year descending. The current (active) year is flagged with `is_current: true`.

**Response `200`**

```json
[
  {
    "id": "uuid",
    "year": 2026,
    "title": "Tanzania DPI Expo 2026",
    "start_date": "2026-11-18T08:00:00Z",
    "end_date": "2026-11-19T18:00:00Z",
    "is_active": true,
    "is_published": true,
    "is_current": true
  },
  {
    "id": "uuid",
    "year": 2025,
    "title": "Tanzania DPI Expo 2025",
    "start_date": "2025-11-20T08:00:00Z",
    "end_date": "2025-11-21T18:00:00Z",
    "is_active": false,
    "is_published": true,
    "is_current": false
  }
]
```

> **Note:** Use `PATCH /api/admin/expo-events/{year}/activate/` to set a year as current — this deactivates all other years.

### 1.9 Manage Hero Images

Add or remove hero images for an event. The `hero_images` array on the ExpoEvent can also be replaced via `PATCH /api/admin/expo-events/{year}/` by passing an array of base64 data URIs or existing paths.

#### Add Hero Image

`POST /api/admin/expo-events/{year}/hero-images/`

**JSON body** (`image_base64` or `image`)

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Multipart body**

Send `file` field with image.

**Response `201`**

```json
{
  "message": "Hero image added.",
  "hero_image": {
    "id": "uuid",
    "image": "http://localhost:8089/media/events/heroes/hero_1.jpg",
    "order": 1,
    "created_at": "...",
    "updated_at": "..."
  }
}
```

#### Remove Hero Image(s)

`DELETE /api/admin/expo-events/{year}/hero-images/`

Accepts one or multiple by `id`(s) or `url`/`path`.

**By id(s)**

```json
{
  "ids": ["uuid-1", "uuid-2"]
}
```

**By url(s)**

```json
{
  "urls": ["http://localhost:8089/media/events/heroes/hero_2.jpg"]
}
```

> **Note:** You can also use `path`, `paths`, `images`, `url`, or `id` keys.

**Response `200`**

```json
{
  "message": "Removed 2 hero image(s).",
  "removed": ["uuid-1", "uuid-2"],
  "hero_images": [
    {
      "id": "uuid",
      "image": "http://localhost:8089/media/events/heroes/hero_1.jpg",
      "order": 1,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

## 2. Event Stats

### 2.1 List / Create / Update / Delete

| Method   | Path                                   |
| -------- | -------------------------------------- |
| `GET`    | `/api/admin/event-stats/?event={uuid}` |
| `POST`   | `/api/admin/event-stats/`              |
| `GET`    | `/api/admin/event-stats/{id}/`         |
| `PATCH`  | `/api/admin/event-stats/{id}/`         |
| `DELETE` | `/api/admin/event-stats/{id}/`         |

**Filter:** `?event={uuid}`

**List response `200`** (paginated)

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "label": "Speakers",
      "value": "50+",
      "order": 1,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

**Create body**

```json
{
  "event": "uuid",
  "label": "Speakers",
  "value": "50+",
  "order": 1
}
```

---

## 3. Focus Areas

### 3.1 List / Create / Update / Delete

| Method   | Path                                   |
| -------- | -------------------------------------- |
| `GET`    | `/api/admin/focus-areas/?event={uuid}` |
| `POST`   | `/api/admin/focus-areas/`              |
| `GET`    | `/api/admin/focus-areas/{id}/`         |
| `PATCH`  | `/api/admin/focus-areas/{id}/`         |
| `DELETE` | `/api/admin/focus-areas/{id}/`         |

**Filter:** `?event={uuid}`

**List response `200`** (paginated)

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "num": "01",
      "title": "Keynotes",
      "description": "Inspiring talks",
      "accent_color": "#F97316",
      "badge_color": "#EA580C",
      "image": "http://localhost:8089/media/events/focus-areas/focus_01.png",
      "order": 1,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

**Create body**

```json
{
  "event": "uuid",
  "num": "01",
  "title": "Keynotes",
  "description": "Inspiring talks",
  "accent_color": "#F97316",
  "badge_color": "#EA580C",
  "image": "data:image/png;base64,iVBOR...",
  "order": 1
}
```

> **Note:** `image` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses.

---

## 4. Partners

### 4.1 List / Create / Update / Delete

| Method   | Path                                          |
| -------- | --------------------------------------------- |
| `GET`    | `/api/admin/partners/?event={uuid}&tier=HOST` |
| `POST`   | `/api/admin/partners/`                        |
| `GET`    | `/api/admin/partners/{id}/`                   |
| `PATCH`  | `/api/admin/partners/{id}/`                   |
| `DELETE` | `/api/admin/partners/{id}/`                   |

**Filters:** `?event={uuid}`, `?tier=HOST|LEAD_PARTNER|PARTNER|MEDIA`  
**Partner tier values:** `HOST`, `LEAD_PARTNER`, `PARTNER`, `MEDIA`

**List response `200`** (paginated)

```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "name": "iDEA",
      "logo": "http://localhost:8089/media/events/logos/idea.png",
      "tier": "HOST",
      "website_url": "https://...",
      "order": 1,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

**Create body**

```json
{
  "event": "uuid",
  "name": "iDEA",
  "logo": "data:image/png;base64,iVBOR...",
  "tier": "HOST",
  "website_url": "https://...",
  "order": 1
}
```

> **Note:** `logo` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses.

---

## 5. Villages

### 5.1 List Villages

`GET /api/admin/villages/?event={uuid}`

**Filter:** `?event={uuid}`

**Response `200`** (paginated)

```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "slug": "govtech",
      "name": "GovTech Village",
      "hall": "Hall A",
      "emoji": "🏛️",
      "theme_color": "#2563EB",
      "tagline": "Transforming Public Services",
      "description": "...",
      "hero_image": "http://localhost:8089/media/events/villages/govtech.png",
      "booths_count": 14,
      "demos_count": 8,
      "order": 1
    }
  ]
}
```

### 5.2 Create Village

`POST /api/admin/villages/`

```json
{
  "event": "uuid",
  "name": "GovTech Village",
  "slug": "govtech",
  "hall": "Hall A",
  "emoji": "🏛️",
  "theme_color": "#2563EB",
  "tagline": "Transforming Public Services",
  "description": "...",
  "why_visit": "...",
  "hero_image": "data:image/png;base64,iVBOR...",
  "stats": [{ "label": "Agencies", "value": "14+" }],
  "order": 1
}
```

> **Note:** `hero_image` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses.

### 5.3 Retrieve Village (with nested booths, schedule, gallery, highlights)

`GET /api/admin/villages/{slug}/`

```json
{
  "id": "uuid",
  "event": "uuid",
  "slug": "govtech",
  "name": "GovTech Village",
  "hall": "Hall A",
  "emoji": "🏛️",
  "theme_color": "#2563EB",
  "tagline": "...",
  "description": "...",
  "why_visit": "...",
  "hero_image": "http://localhost:8089/media/events/villages/govtech.png",
  "stats": [{ "label": "Agencies", "value": "14+" }],
  "booths": [
    {
      "id": "uuid",
      "village": "uuid",
      "name": "GovNet & e-GA Gateway",
      "org": "e-Government Authority",
      "booth_number": "A-01",
      "tag": "Infrastructure",
      "description": "Interoperability middleware.",
      "live_demo": "10:30 AM — Live Demo",
      "website_url": "https://...",
      "logo": "http://localhost:8089/media/events/booth-logos/govtech_booth_1.png",
      "is_featured": true,
      "order": 1
    }
  ],
  "schedule": [
    {
      "id": "uuid",
      "village": "uuid",
      "time": "09:30 AM",
      "title": "Open-Source Public Digital Stack",
      "presenter": "Eng. Baraka Mtalo",
      "booth_or_stage": "Stage A",
      "day_number": 1,
      "order": 1
    }
  ],
  "gallery": [
    {
      "id": "uuid",
      "village": "uuid",
      "image": "http://localhost:8089/media/events/gallery/govtech_gallery_1.png",
      "title": "Citizen Portal Showcase",
      "caption": "One-stop government services",
      "edition_year": 2026,
      "order": 1
    }
  ],
  "highlights": [
    {
      "id": "uuid",
      "village": "uuid",
      "icon": "smart_display",
      "title": "Live Production Demos",
      "description": "Experience hands-on workflows running on real infrastructure testbeds.",
      "order": 1
    }
  ],
  "order": 1
}
```

### 5.4 Update / Delete

`PATCH /api/admin/villages/{slug}/` | `DELETE /api/admin/villages/{slug}/`

---

## 6. Village Booths

| Method   | Path                                        |
| -------- | ------------------------------------------- |
| `GET`    | `/api/admin/village-booths/?village={uuid}` |
| `POST`   | `/api/admin/village-booths/`                |
| `PATCH`  | `/api/admin/village-booths/{id}/`           |
| `DELETE` | `/api/admin/village-booths/{id}/`           |

**Filter:** `?village={uuid}`

**List response `200`** (paginated)

```json
{
  "count": 14,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "village": "uuid",
      "name": "GovNet & e-GA Gateway",
      "org": "e-Government Authority",
      "booth_number": "A-01",
      "tag": "Infrastructure",
      "description": "Interoperability middleware.",
      "live_demo": "10:30 AM — Live Demo",
      "website_url": "https://...",
      "logo": "http://localhost:8089/media/events/booth-logos/govtech_booth_1.png",
      "is_featured": true,
      "order": 1
    }
  ]
}
```

**Create body**

```json
{
  "village": "uuid",
  "name": "GovNet & e-GA Gateway",
  "org": "e-Government Authority",
  "booth_number": "A-01",
  "tag": "Infrastructure",
  "description": "Interoperability middleware.",
  "live_demo": "10:30 AM — Live Demo",
  "website_url": "https://...",
  "logo": "data:image/png;base64,iVBOR...",
  "is_featured": true,
  "order": 1
}
```

> **Note:** `logo` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses.

---

## 7. Village Schedules

Village-specific demo schedules.

| Method   | Path                                                        |
| -------- | ----------------------------------------------------------- |
| `GET`    | `/api/admin/village-schedules/?village={uuid}&day_number=1` |
| `GET`    | `/api/admin/village-schedules/{id}/`                        |
| `POST`   | `/api/admin/village-schedules/`                             |
| `PATCH`  | `/api/admin/village-schedules/{id}/`                        |
| `DELETE` | `/api/admin/village-schedules/{id}/`                        |

**Filters:** `?village={uuid}`, `?day_number=1`

**List response `200`** (paginated)

```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "village": "uuid",
      "time": "09:30 AM",
      "title": "Open-Source Public Digital Stack",
      "presenter": "Eng. Baraka Mtalo",
      "booth_or_stage": "Stage A",
      "day_number": 1,
      "order": 1
    }
  ]
}
```

**Create body**

```json
{
  "village": "uuid",
  "time": "09:30 AM",
  "title": "Open-Source Public Digital Stack",
  "presenter": "Eng. Baraka Mtalo",
  "booth_or_stage": "Stage A",
  "day_number": 1,
  "order": 1
}
```

---

## 8. Village Galleries

| Method   | Path                                                             |
| -------- | ---------------------------------------------------------------- |
| `GET`    | `/api/admin/village-galleries/?village={uuid}&edition_year=2026` |
| `POST`   | `/api/admin/village-galleries/`                                  |
| `PATCH`  | `/api/admin/village-galleries/{id}/`                             |
| `DELETE` | `/api/admin/village-galleries/{id}/`                             |

**Filters:** `?village={uuid}`, `?edition_year=2026`

**List response `200`** (paginated)

```json
{
  "count": 24,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "village": "uuid",
      "image": "http://localhost:8089/media/events/gallery/govtech_gallery_1.png",
      "title": "Citizen Portal Showcase",
      "caption": "One-stop government services",
      "edition_year": 2026,
      "order": 1
    }
  ]
}
```

**Create body**

```json
{
  "village": "uuid",
  "image": "data:image/png;base64,iVBOR...",
  "title": "Citizen Portal Showcase",
  "caption": "One-stop government services",
  "edition_year": 2026,
  "order": 1
}
```

> **Note:** `image` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses.

---

## 9. Booth Applications

### 9.1 List Applications

`GET /api/admin/booth-applications/?event={uuid}&status=PENDING_REVIEW`

**Filters:** `?event={uuid}`, `?village={uuid}`, `?status=PENDING_REVIEW|APPROVED|ALLOCATED|REJECTED`  
**Search:** `?search=company_name` (searches `company_name`, `email`, `reference_no`)  
**Booth application status values:** `PENDING_REVIEW`, `APPROVED`, `ALLOCATED`, `REJECTED`

**List response `200`** (paginated)

```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "reference_no": "TZ-DPI-BOOTH-0BAD1DFA",
      "event": "uuid",
      "village": "uuid",
      "company_name": "Tech Co",
      "company_website": "https://...",
      "company_sector": "Fintech",
      "booth_package": "STANDARD",
      "showcase_title": "AI Demo",
      "showcase_desc": "AI powered solutions",
      "tech_requirements": ["..."],
      "co_exhibitors": "",
      "first_name": "Alice",
      "last_name": "Kimaro",
      "email": "alice@techco.com",
      "phone": "+255...",
      "job_title": "Head of Partnerships",
      "country": "Tanzania",
      "status": "PENDING_REVIEW",
      "assigned_booth_no": "",
      "admin_notes": "",
      "agree_terms": true,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

### 9.2 Retrieve Application

`GET /api/admin/booth-applications/{id}/`

```json
{
  "id": "uuid",
  "reference_no": "TZ-DPI-BOOTH-0BAD1DFA",
  "event": "uuid",
  "village": "uuid",
  "company_name": "Tech Co",
  "company_website": "https://...",
  "company_sector": "Fintech",
  "booth_package": "STANDARD",
  "showcase_title": "AI Demo",
  "showcase_desc": "AI powered solutions",
  "tech_requirements": ["..."],
  "co_exhibitors": "",
  "first_name": "Alice",
  "last_name": "Kimaro",
  "email": "alice@techco.com",
  "phone": "+255...",
  "job_title": "Head of Partnerships",
  "country": "Tanzania",
  "status": "PENDING_REVIEW",
  "assigned_booth_no": "",
  "admin_notes": "",
  "agree_terms": true,
  "created_at": "...",
  "updated_at": "..."
}
```

### 9.3 Update Application Status & Allocate Booth

`PATCH /api/admin/booth-applications/{id}/status/`

**Request body**

```json
{
  "status": "APPROVED",
  "assigned_booth_no": "A-04",
  "admin_notes": "Approved for Hall A tier."
}
```

**Response `200`**

```json
{
  "success": true,
  "data": { "id": "uuid", "status": "APPROVED", "assigned_booth_no": "A-04", ... }
}
```

### 9.4 Delete Application

`DELETE /api/admin/booth-applications/{id}/` — `204 No Content`

---

## 10. Registrations

### 10.1 List Registrations

`GET /api/admin/registrations/?event={uuid}&type=GUEST&status=CONFIRMED`

**Filters:** `?event={uuid}`, `?type=GUEST|SPEAKER|VOLUNTEER`, `?status=CONFIRMED|PENDING_REVIEW|APPROVED|WAITLIST|REJECTED`  
**Search:** `?search=john` (searches `first_name`, `last_name`, `email`, `reference_no`)

**List response `200`** (paginated)

```json
{
  "count": 8420,
  "next": "http://...&page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "reference_no": "TZ-DPI-GUE-BB20C79C",
      "event": "uuid",
      "type": "GUEST",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+255123456789",
      "country": "Tanzania",
      "organization": "Test Org",
      "extra_data": { "guest_category": "", "dietary_reqs": "" },
      "status": "CONFIRMED",
      "badge_code": "QR-TZ-DPI-GUE-BB20C79C",
      "agree_terms": true,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

### 10.2 Retrieve / Update / Delete

| Method   | Path                             |
| -------- | -------------------------------- |
| `GET`    | `/api/admin/registrations/{id}/` |
| `PATCH`  | `/api/admin/registrations/{id}/` |
| `DELETE` | `/api/admin/registrations/{id}/` |

**Retrieve response `200`**

```json
{
  "id": "uuid",
  "reference_no": "TZ-DPI-GUE-BB20C79C",
  "event": "uuid",
  "type": "GUEST",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+255123456789",
  "country": "Tanzania",
  "organization": "Test Org",
  "extra_data": { "guest_category": "", "dietary_reqs": "" },
  "status": "CONFIRMED",
  "badge_code": "QR-TZ-DPI-GUE-BB20C79C",
  "agree_terms": true,
  "created_at": "...",
  "updated_at": "..."
}
```

**Registration status values:** `CONFIRMED`, `PENDING_REVIEW`, `APPROVED`, `WAITLIST`, `REJECTED`  
**Registration type values:** `GUEST`, `SPEAKER`, `VOLUNTEER`

### 10.3 Approve Registration

`POST /api/admin/registrations/{id}/approve/`

Approves the registration. For `SPEAKER` type, it also creates a new `Speaker` record (confirmed) and returns it.

**Response `200`**

```json
{
  "message": "Registration approved.",
  "registration": {
    "id": "uuid",
    "reference_no": "TZ-DPI-SPE-041C0A9D",
    "type": "SPEAKER",
    "first_name": "Miriam",
    "last_name": "Griffin",
    "status": "APPROVED",
    ...
  },
  "speaker": {
    "id": "uuid",
    "event": "uuid",
    "name": "Miriam Griffin",
    "title": "Quis esse atque quae",
    "org": "Merritt Green LLC",
    "initials": "MG",
    "color": "#2563EB",
    "accent_light": "#DBEAFE",
    "photo": null,
    "bio": "Incididunt voluptate",
    "order": 6,
    "is_confirmed": true,
    "is_approved": true
  }
}
```

### 10.4 Reject Registration

`POST /api/admin/registrations/{id}/reject/`

**Response `200`**

```json
{
  "message": "Registration rejected.",
  "registration": {
    "id": "uuid",
    "status": "REJECTED",
    ...
  }
}
```

---

## 11. Speakers

### 11.1 List / Create / Update / Delete

| Method   | Path                                                  |
| -------- | ----------------------------------------------------- |
| `GET`    | `/api/admin/speakers/?event={uuid}&is_confirmed=true` |
| `POST`   | `/api/admin/speakers/`                                |
| `PATCH`  | `/api/admin/speakers/{id}/`                           |
| `DELETE` | `/api/admin/speakers/{id}/`                           |

**Filters:** `?event={uuid}`, `?is_confirmed=true|false`

**List response `200`** (paginated)

```json
{
  "count": 48,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "name": "Dr. Fatma Hassan",
      "title": "Minister of ICT",
      "org": "Government of Tanzania",
      "initials": "FH",
      "color": "#1E40AF",
      "accent_light": "#DBEAFE",
      "photo": "http://localhost:8089/media/events/speakers/FH.png",
      "bio": "Leading national telecommunication transformation.",
      "order": 1,
      "is_confirmed": true,
      "is_approved": true
    }
  ]
}
```

**Create body**

```json
{
  "event": "uuid",
  "name": "Dr. Fatma Hassan",
  "title": "Minister of ICT",
  "org": "Government of Tanzania",
  "initials": "FH",
  "color": "#1E40AF",
  "accent_light": "#DBEAFE",
  "photo": "data:image/png;base64,iVBOR...",
  "bio": "Leading national telecommunication transformation.",
  "order": 1,
  "is_confirmed": true
}
```

> **Note:** `photo` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses.

### 11.2 Approve Speaker

`POST /api/admin/speakers/{id}/approve/`

Sets `is_confirmed`/`is_approved` to `true` for an existing speaker.

**Response `200`** — the updated `Speaker` object.

### 11.3 Unconfirm Speaker

`POST /api/admin/speakers/{id}/unconfirm/`

Sets `is_confirmed`/`is_approved` to `false` for an existing speaker.

**Response `200`** — the updated `Speaker` object.

---

## 12. Sessions

Event-wide conference sessions (keynotes, panels, workshops, breaks, exhibitions).

### 12.1 List / Create / Update / Delete

| Method   | Path                                                          |
| -------- | ------------------------------------------------------------- |
| `GET`    | `/api/admin/sessions/?event={uuid}&day_number=1&type=KEYNOTE` |
| `GET`    | `/api/admin/sessions/{id}/`                                   |
| `POST`   | `/api/admin/sessions/`                                        |
| `PATCH`  | `/api/admin/sessions/{id}/`                                   |
| `DELETE` | `/api/admin/sessions/{id}/`                                   |

**Filters:** `?event={uuid}`, `?day_number=1`, `?type=KEYNOTE|PANEL|WORKSHOP|BREAK|EXHIBITION`

**List response `200`** (paginated)

```json
{
  "count": 32,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "day_number": 1,
      "start_time": "09:00",
      "end_time": "10:00",
      "title": "Opening Keynote",
      "type": "KEYNOTE",
      "speaker": {
        "id": "uuid",
        "event": "uuid",
        "name": "Dr. Fatma Hassan",
        "title": "Minister of ICT",
        "org": "Government of Tanzania",
        "initials": "FH",
        "color": "#1E40AF",
        "accent_light": "#DBEAFE",
        "photo": "http://localhost:8089/media/events/speakers/FH.png",
        "bio": "...",
        "order": 1,
        "is_confirmed": true
      },
      "speaker_id": "uuid",
      "speaker_text": "",
      "location": "Main Hall",
      "order": 1
    }
  ]
}
```

**Create body**

```json
{
  "event": "uuid",
  "day_number": 1,
  "start_time": "09:00",
  "end_time": "10:00",
  "title": "Opening Keynote",
  "type": "KEYNOTE",
  "speaker_id": "uuid",
  "speaker_text": "",
  "location": "Main Hall",
  "order": 1
}
```

**Response** includes nested `speaker` object (read-only) and writable `speaker_id`.

**Session type values:** `KEYNOTE`, `PANEL`, `WORKSHOP`, `BREAK`, `EXHIBITION`

---

## 13. Media Assets

### 13.1 Upload File (Base64 JSON)

`POST /api/admin/media-assets/`

**Content-Type:** `application/json`

Supports **base64-encoded** file uploads via JSON. The `file_base64` field accepts data URIs (`data:image/...;base64,...`). The file is saved to the filesystem via Django `FileField` and the response returns the file URL.

| Field         | Type   | Description                                                  |
| ------------- | ------ | ------------------------------------------------------------ |
| `file_base64` | String | Base64 data URI: `data:image/png;base64,iVBOR...`            |
| `folder`      | String | `heroes`, `speakers`, `villages`, `gallery`, `logos`, `docs` |
| `altText`     | String | Accessibility description                                    |
| `eventId`     | UUID   | Optional, links to event                                     |

**Request example**

```json
{
  "file_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "folder": "gallery",
  "altText": "GovTech Village keynote stage",
  "eventId": "3df2e41b-1cb8-4d1d-90c2-8042e72abea7"
}
```

**Response `201`** (includes both snake_case and camelCase fields)

```json
{
  "id": "uuid",
  "event": "uuid",
  "eventId": "uuid",
  "original_name": "upload_a1b2c3d4.png",
  "originalName": "upload_a1b2c3d4.png",
  "file_name": "upload_a1b2c3d4.png",
  "fileName": "upload_a1b2c3d4.png",
  "mime_type": "image/png",
  "mimeType": "image/png",
  "size_bytes": 1420580,
  "sizeBytes": 1420580,
  "folder": "gallery",
  "file": "http://localhost:8089/media/events/media/upload_a1b2c3d4.png",
  "thumbnail": null,
  "alt_text": "GovTech Village keynote stage",
  "alt_text_read": "GovTech Village keynote stage",
  "altText": "GovTech Village keynote stage",
  "width": 1920,
  "height": 1080,
  "dimensions": { "width": 1920, "height": 1080 },
  "created_at": "...",
  "createdAt": "..."
}
```

> **Note:** `file_base64` accepts base64 data URIs (`data:image/...;base64,...`). The `file` and `thumbnail` fields in the response are Django `FileField`/`ImageField` absolute URLs pointing to the filesystem. Image dimensions (`width`, `height`, `dimensions`) are automatically extracted on upload.

### 13.2 Upload File (Multipart)

`POST /api/admin/media-assets/`

**Content-Type:** `multipart/form-data`

Also supports traditional multipart file uploads. Use `file_base64` as the multipart file field name. Same other fields as above.

### 13.3 List / Update / Delete

| Method   | Path                                                   |
| -------- | ------------------------------------------------------ |
| `GET`    | `/api/admin/media-assets/?event={uuid}&folder=gallery` |
| `PATCH`  | `/api/admin/media-assets/{id}/`                        |
| `DELETE` | `/api/admin/media-assets/{id}/`                        |

### 13.4 Media Library Browser

`GET /api/admin/files/?folder=gallery&search=keynote&eventId={uuid}&page=1&limit=24`

**Query params:** `folder`, `search`, `eventId`, `page`, `limit` (default 24)

**Response `200`** (paginated, snake_case fields)

```json
{
  "count": 148,
  "next": "http://...&page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "event": "uuid",
      "original_name": "photo.jpg",
      "file_name": "events/gallery/photo.jpg",
      "mime_type": "image/jpeg",
      "size_bytes": 1420580,
      "folder": "gallery",
      "file": "http://localhost:8089/media/events/gallery/photo.jpg",
      "thumbnail": null,
      "alt_text": "Caption",
      "width": null,
      "height": null,
      "created_at": "..."
    }
  ]
}
```

> **Note:** Query params use camelCase (`eventId`). Response fields `file` and `thumbnail` are Django `FileField`/`ImageField` absolute URLs.

---

## 14. Dashboard Metrics

`GET /api/admin/events/{year}/metrics/`

**Response `200`**

```json
{
  "success": true,
  "metrics": {
    "totalRegistrations": 8420,
    "breakdown": {
      "guests": 7850,
      "booths": 52,
      "speakers": 48,
      "volunteers": 470
    },
    "villageOccupancy": [
      {
        "slug": "govtech",
        "name": "GovTech Village",
        "allocatedBooths": 14,
        "capacity": 16,
        "occupancyRate": "87.5%"
      }
    ],
    "pendingBoothApplications": 7
  }
}
```

---

## 15. Badge Export (CSV)

`GET /api/admin/events/{year}/export/badges/?type=all`

**Query param:** `type` — `all`, `GUEST`, `SPEAKER`, `VOLUNTEER`

**Response `200`** — `text/csv` attachment

```
RefNo,Name,Email,Organization,Category,BadgeCode,Status
TZ-DPI-GUE-BB20C79C,John Doe,john@example.com,Test Org,GUEST,QR-TZ-DPI-GUE-BB20C79C,CONFIRMED
```

---

## 16. Event Hero Images

### 16.1 List / Create / Update / Delete

| Method   | Path                                         |
| -------- | -------------------------------------------- |
| `GET`    | `/api/admin/event-hero-images/?event={uuid}` |
| `POST`   | `/api/admin/event-hero-images/`              |
| `GET`    | `/api/admin/event-hero-images/{id}/`         |
| `PATCH`  | `/api/admin/event-hero-images/{id}/`         |
| `DELETE` | `/api/admin/event-hero-images/{id}/`         |

**Filter:** `?event={uuid}`

**List response `200`** (paginated)

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "image": "http://localhost:8089/media/events/heroes/hero_1.jpg",
      "order": 1,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

**Create body**

```json
{
  "event": "uuid",
  "image": "data:image/png;base64,iVBOR...",
  "order": 1
}
```

> **Note:** `image` is an `ImageField` — accepts base64 data URI on create/update, returns absolute file URL in responses. The `event` field is write-only.

---

## 17. Village Highlights

### 17.1 List / Create / Update / Delete

| Method   | Path                                            |
| -------- | ----------------------------------------------- |
| `GET`    | `/api/admin/village-highlights/?village={uuid}` |
| `POST`   | `/api/admin/village-highlights/`                |
| `GET`    | `/api/admin/village-highlights/{id}/`           |
| `PATCH`  | `/api/admin/village-highlights/{id}/`           |
| `DELETE` | `/api/admin/village-highlights/{id}/`           |

**Filter:** `?village={uuid}`

**List response `200`** (paginated)

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "village": "uuid",
      "icon": "smart_display",
      "title": "Live Production Demos",
      "description": "Experience hands-on workflows running on real infrastructure testbeds.",
      "order": 1
    }
  ]
}
```

**Create body**

```json
{
  "village": "uuid",
  "icon": "smart_display",
  "title": "Live Production Demos",
  "description": "Experience hands-on workflows running on real infrastructure testbeds.",
  "order": 1
}
```
