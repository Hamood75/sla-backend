# Posts API (Blog & Podcast)

Posts are a single CMS model covering two content types: `blog` and `podcast`.

## Public endpoints

Base URL: `/api/posts/` (read-only, anonymous OK)

| Method | Endpoint             | Description                       |
| ------ | -------------------- | --------------------------------- |
| GET    | `/api/posts/`        | List published posts              |
| GET    | `/api/posts/{slug}/` | Retrieve a published post by slug |

Only `is_published=true` posts are returned.

## Admin (backoffice) endpoints

Base URL: `/api/admin/posts/` — requires a backoffice JWT token (`Authorization: Bearer <token>`). Returns all posts regardless of `is_published`.

| Method    | Endpoint                   | Description             |
| --------- | -------------------------- | ----------------------- |
| GET       | `/api/admin/posts/`        | List all posts          |
| GET       | `/api/admin/posts/{slug}/` | Retrieve a post by slug |
| POST      | `/api/admin/posts/`        | Create a post           |
| PUT/PATCH | `/api/admin/posts/{slug}/` | Update a post           |
| DELETE    | `/api/admin/posts/{slug}/` | Delete a post           |

## Filters

- `?post_type=blog` or `?post_type=podcast`
- `?search=<term>` — searches `title`, `slug`, `excerpt`

## Fields

| Field            | Type     | Notes                                                          |
| ---------------- | -------- | -------------------------------------------------------------- |
| `post_type`      | string   | `blog` or `podcast` (required)                                 |
| `title`          | string   |                                                                |
| `slug`           | string   | Unique, used for lookup                                        |
| `excerpt`        | text     | Short summary for lists                                        |
| `body`           | text     | Full post content                                              |
| `cover_image`    | image    | Optional cover                                                 |
| `episode_number` | int      | Podcast episodes only                                          |
| `scheduled_at`   | datetime | Podcasts: when the live session happens                        |
| `live_join_url`  | URL      | Podcasts: link to join live (e.g. Google Meet, YouTube Live)   |
| `recording_url`  | URL      | Podcasts: link to the recorded episode (e.g. Spotify, YouTube) |
| `is_published`   | bool     | Default `true`                                                 |
| `order`          | int      | Sort order                                                     |

## Create a podcast episode

```http
POST /api/admin/posts/
Authorization: Bearer <backoffice-token>
Content-Type: multipart/form-data

post_type=podcast
title=TEHAMA Roundtable — Episode 001
slug=tehama-roundtable-001
excerpt=Kwa nini kampuni za TEHAMA Tanzania hazikui na kuwa Big Tech?
episode_number=1
scheduled_at=2026-10-11T19:00:00+03:00
live_join_url=https://meet.google.com/pfc-sdye-njf
is_published=true
```

Response `201`:

```json
{
  "id": 1,
  "post_type": "podcast",
  "title": "TEHAMA Roundtable — Episode 001",
  "slug": "tehama-roundtable-001",
  "excerpt": "Kwa nini kampuni za TEHAMA Tanzania hazikui na kuwa Big Tech?",
  "body": "",
  "cover_image": null,
  "episode_number": 1,
  "scheduled_at": "2026-10-11T19:00:00+03:00",
  "live_join_url": "https://meet.google.com/pfc-sdye-njf",
  "recording_url": "",
  "is_published": true,
  "order": 0,
  "created_at": "...",
  "updated_at": "..."
}
```

## Frontend notes

- For `post_type=podcast`, render `live_join_url` as a "Join Live" button while `scheduled_at` is in the future; show `recording_url` afterwards.
- `live_join_url` and `recording_url` are optional — hide the buttons when empty.
