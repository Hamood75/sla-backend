# Events Public API Guide

All public endpoints are open (no auth required).  
Base URL: `/api/events/`

All image and file fields return **absolute URLs** (e.g. `"http://localhost:8089/media/events/villages/govtech.png"`) pointing to files stored via Django `ImageField`/`FileField`.

---

## 1. Landing Page

`GET /api/events/landing/`

Returns aggregated data for the event landing page: active + published event, stats, villages, gallery, focus areas, partners, and featured speakers.

**Response `200`**

```json
{
  "success": true,
  "data": {
    "event": {
      "id": "uuid",
      "year": 2026,
      "title": "Tanzania DPI Expo 2026",
      "tagline": "Building Digital Foundation",
      "description": "# Two Days of Innovation...",
      "startDate": "2026-11-18T11:00:00+03:00",
      "endDate": "2026-11-19T21:00:00+03:00",
      "venue": {
        "name": "Diamond Jubilee Expo Center",
        "address": "Ohio Street, Dar es Salaam",
        "latitude": -6.8161,
        "longitude": 39.2804
      },
      "heroImages": [
        {
          "id": "uuid",
          "image": "http://localhost:8089/media/events/heroes/hero_1.jpg",
          "order": 1,
          "created_at": "...",
          "updated_at": "..."
        }
      ]
    },
    "stats": [{ "label": "Speakers", "value": "50+" }],
    "villages": [
      {
        "id": "uuid",
        "name": "GovTech Village",
        "slug": "govtech",
        "hall": "Hall A",
        "emoji": "🏛️",
        "color": "#2563EB",
        "img": "http://localhost:8089/media/events/villages/govtech.png",
        "desc": "Live demos of e-Government platforms...",
        "booths": 14,
        "demos": 8,
        "order": 1
      }
    ],
    "gallery": [
      {
        "id": "uuid",
        "url": "http://localhost:8089/media/events/gallery/govtech_gallery_1.png",
        "title": "Photo",
        "layout": "standard"
      }
    ],
    "focusAreas": [
      {
        "id": "uuid",
        "num": "01",
        "title": "Keynotes",
        "desc": "Inspiring talks",
        "accentColor": "#F97316",
        "badgeColor": "#EA580C",
        "img": "http://localhost:8089/media/events/focus-areas/focus_01.png"
      }
    ],
    "partners": [
      {
        "id": "uuid",
        "name": "iDEA",
        "logo": "http://localhost:8089/media/events/logos/idea.png"
      }
    ],
    "featuredSpeakers": [
      {
        "id": "uuid",
        "name": "Dr. Fatma Hassan",
        "title": "Minister of ICT",
        "org": "Government of Tanzania",
        "initials": "FH",
        "color": "#1E40AF",
        "accentLight": "#DBEAFE",
        "photo": "http://localhost:8089/media/events/speakers/FH.png",
        "bio": "Leading national telecommunication transformation.",
        "order": 1
      }
    ]
  }
}
```

**Response `404`** — No active or upcoming published event found.

```json
{
  "success": false,
  "error": "No active or upcoming event found"
}
```

---

## 2. Event Editions

`GET /api/events/editions/`

Returns all published event editions/years, ordered by year descending. The current (active) year is flagged with `is_current: true`. `current_year` at the top level indicates the active year (or `null` if none active).

**Response `200`**

```json
{
  "success": true,
  "count": 2,
  "current_year": 2026,
  "editions": [
    {
      "id": "uuid",
      "year": 2026,
      "title": "Tanzania DPI Expo 2026",
      "tagline": "Building Digital Foundation",
      "start_date": "2026-11-18T08:00:00Z",
      "end_date": "2026-11-19T18:00:00Z",
      "venue_name": "Diamond Jubilee Hall",
      "is_current": true
    },
    {
      "id": "uuid",
      "year": 2025,
      "title": "Tanzania DPI Expo 2025",
      "tagline": "Digital Transformation in Action",
      "start_date": "2025-11-20T08:00:00Z",
      "end_date": "2025-11-21T18:00:00Z",
      "venue_name": "Diamond Jubilee Hall",
      "is_current": false
    }
  ]
}
```

---

## 3. Villages List

`GET /api/events/{year}/villages/`

Returns all villages for a published event, ordered by `order`.

**Response `200`**

```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": "uuid",
      "slug": "govtech",
      "name": "GovTech Village",
      "hall": "Hall A",
      "emoji": "🏛️",
      "themeColor": "#2563EB",
      "tagline": "Transforming Public Services",
      "desc": "Live demos of e-Government platforms...",
      "heroImage": "http://localhost:8089/media/events/villages/govtech.png",
      "boothsCount": 14,
      "demosCount": 8,
      "order": 1
    }
  ]
}
```

---

## 4. Village Detail

`GET /api/events/{year}/villages/{slug}/`

Returns full village details with nested booths, schedule, gallery, whyVisit, and keyHighlights.

**Response `200`**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "slug": "govtech",
    "name": "GovTech Village",
    "hall": "Hall A",
    "emoji": "🏛️",
    "themeColor": "#2563EB",
    "tagline": "Transforming Public Services",
    "description": "...",
    "whyVisit": "...",
    "keyHighlights": [
      {
        "id": "uuid",
        "icon": "smart_display",
        "title": "Live Production Demos",
        "description": "Experience hands-on workflows running on real infrastructure testbeds.",
        "order": 1
      }
    ],
    "heroImage": "http://localhost:8089/media/events/villages/govtech.png",
    "stats": [{ "label": "Participating Agencies", "value": "14+" }],
    "booths": [
      {
        "id": "uuid",
        "name": "GovNet & e-GA Gateway",
        "org": "e-Government Authority",
        "boothNo": "A-01",
        "tag": "Infrastructure",
        "desc": "Interoperability middleware.",
        "liveDemo": "10:30 AM — Live Demo",
        "websiteUrl": "https://...",
        "logoUrl": "http://localhost:8089/media/events/booth-logos/govtech_booth_1.png",
        "isFeatured": true
      }
    ],
    "schedule": [
      {
        "id": "uuid",
        "time": "09:30 AM",
        "title": "Open-Source Public Digital Stack",
        "presenter": "Eng. Baraka Mtalo (eGA)",
        "booth": "Stage A"
      }
    ],
    "gallery": [
      {
        "id": "uuid",
        "url": "http://localhost:8089/media/events/gallery/govtech_gallery_1.png",
        "title": "Citizen Portal Showcase",
        "caption": "One-stop government services"
      }
    ],
    "order": 1
  }
}
```

**Response `404`** — Event not found, not published, or village slug not found.

---

## 5. Speakers

`GET /api/events/{year}/speakers/`

Returns confirmed speakers for a published event, ordered by `order`.

**Response `200`**

```json
{
  "success": true,
  "count": 6,
  "data": [
    {
      "id": "uuid",
      "name": "Dr. Fatma Hassan",
      "title": "Minister of ICT",
      "org": "Government of Tanzania",
      "initials": "FH",
      "color": "#1E40AF",
      "accentLight": "#DBEAFE",
      "photo": "http://localhost:8089/media/events/speakers/FH.png",
      "bio": "Leading national telecommunication transformation.",
      "order": 1
    }
  ]
}
```

---

## 6. Schedule

`GET /api/events/{year}/schedule/`

Returns the conference schedule grouped by day.

**Response `200`**

```json
{
  "success": true,
  "days": [
    {
      "dayNumber": 1,
      "date": "November 18, 2026",
      "dayLabel": "Day 1",
      "sessions": [
        {
          "id": "uuid",
          "time": "09:00 – 10:00",
          "title": "Opening Keynote",
          "type": "KEYNOTE",
          "speaker": "Dr. Fatma Hassan",
          "location": "Main Hall"
        }
      ]
    },
    {
      "dayNumber": 2,
      "date": "November 19, 2026",
      "dayLabel": "Day 2",
      "sessions": [
        {
          "id": "uuid",
          "time": "10:00 – 11:00",
          "title": "DPI Panel Discussion",
          "type": "PANEL",
          "speaker": "Dr. Fatma Hassan",
          "location": "Room B"
        }
      ]
    }
  ]
}
```

**Session types:** `KEYNOTE`, `PANEL`, `WORKSHOP`, `BREAK`, `NETWORKING`

**Note:** `speaker` field returns the speaker's name if linked, otherwise falls back to `speaker_text`.

---

## 7. Guest Registration

`POST /api/events/{year}/register/guest/`

**Request body**

```json
{
  "first_name": "John",
  "last_name": "Kamau",
  "email": "john.kamau@example.org",
  "phone": "+255712987654",
  "country": "Tanzania",
  "organization": "e-Government Authority",
  "guest_category": "Policymaker / Government Official",
  "dietary_reqs": "Vegetarian",
  "agree_terms": true
}
```

**Required fields:** `first_name`, `last_name`, `email`, `phone`, `country`  
**Optional fields:** `organization`, `guest_category`, `dietary_reqs`, `agree_terms` (default `true`)

**Response `201`**

```json
{
  "success": true,
  "referenceNo": "TZ-DPI-GUE-BB20C79C",
  "badgeCode": "QR-TZ-DPI-GUE-BB20C79C",
  "message": "Registration confirmed. Entry badge sent to your email.",
  "data": {
    "id": "uuid",
    "type": "GUEST",
    "name": "John Kamau",
    "email": "john.kamau@example.org",
    "status": "CONFIRMED"
  }
}
```

---

## 8. Speaker Registration

`POST /api/events/{year}/register/speaker/`

**Request body**

```json
{
  "first_name": "Dr. Fatma",
  "last_name": "Hassan",
  "email": "fatma.hassan@example.org",
  "phone": "+255712987654",
  "country": "Tanzania",
  "organization": "Ministry of ICT",
  "talk_title": "Tanzania's Digital Public Infrastructure Roadmap",
  "talk_abstract": "A comprehensive overview of Tanzania's DPI strategy...",
  "speaker_bio": "Dr. Fatma Hassan is the Minister of ICT...",
  "linked_in": "https://linkedin.com/in/fatma",
  "previous_speaking": "Keynote at Africa Tech Summit 2025",
  "agree_terms": true
}
```

**Required fields:** `first_name`, `last_name`, `email`, `phone`, `country`, `talk_title`, `talk_abstract`, `speaker_bio`  
**Optional fields:** `organization`, `linked_in`, `previous_speaking`, `agree_terms` (default `true`)

**Response `201`**

```json
{
  "success": true,
  "referenceNo": "TZ-DPI-SPE-6C54974A",
  "badgeCode": "QR-TZ-DPI-SPE-6C54974A",
  "message": null,
  "data": {
    "id": "uuid",
    "type": "SPEAKER",
    "name": "Dr. Fatma Hassan",
    "email": "fatma.hassan@example.org",
    "status": "CONFIRMED"
  }
}
```

---

## 9. Volunteer Registration

`POST /api/events/{year}/register/volunteer/`

**Request body**

```json
{
  "first_name": "Bob",
  "last_name": "Volunteer",
  "email": "bob@example.com",
  "phone": "+255712987654",
  "country": "Tanzania",
  "organization": "University of Dar es Salaam",
  "volunteer_role": "Logistics",
  "availability": ["Day 1", "Day 2"],
  "skills": "Event coordination, first aid",
  "motivation": "I want to contribute to Tanzania's digital future.",
  "agree_terms": true
}
```

**Required fields:** `first_name`, `last_name`, `email`, `phone`, `country`, `volunteer_role`, `availability` (array of strings)  
**Optional fields:** `organization`, `skills`, `motivation`, `agree_terms` (default `true`)

**Response `201`**

```json
{
  "success": true,
  "referenceNo": "TZ-DPI-VOL-1BEE82DC",
  "badgeCode": "QR-TZ-DPI-VOL-1BEE82DC",
  "message": null,
  "data": {
    "id": "uuid",
    "type": "VOLUNTEER",
    "name": "Bob Volunteer",
    "email": "bob@example.com",
    "status": "CONFIRMED"
  }
}
```

---

## 10. Booth Registration

`POST /api/events/{year}/register/booth/`

Submit a booth/exhibitor application for a specific village.

**Request body**

```json
{
  "selected_village": "govtech",
  "company_name": "Selcom Paytech Tanzania Ltd",
  "company_website": "https://selcom.net",
  "company_sector": "Fintech & Digital Payments",
  "booth_package": "Premium Double Booth (6m x 3m)",
  "showcase_title": "Interoperable Micro-Merchant Payment QR Stack",
  "showcase_description": "Live point-of-sale checkout simulations...",
  "tech_requirements": [
    "Dedicated High-Speed Wired LAN Connection (50 Mbps)",
    "55\" 4K Smart Display Screen with Floor Stand"
  ],
  "co_exhibitors": "In partnership with Bank of Tanzania (BoT)",
  "contact": {
    "firstName": "Amina",
    "lastName": "Kimaro",
    "email": "amina.kimaro@selcom.net",
    "phone": "+255712345678",
    "jobTitle": "Head of Partnerships",
    "country": "Tanzania"
  },
  "agree_terms": true
}
```

**Required fields:** `selected_village` (must be a valid village slug for the event), `company_name`, `booth_package`, `showcase_title`, `showcase_description`, `contact` (object)  
**Optional fields:** `company_website`, `company_sector`, `tech_requirements` (array), `co_exhibitors`, `agree_terms` (default `true`)

**Response `201`**

```json
{
  "success": true,
  "referenceNo": "TZ-DPI-BOOTH-0BAD1DFA",
  "message": "Your booth application for GovTech Village has been received.",
  "data": {
    "id": "uuid",
    "referenceNo": "TZ-DPI-BOOTH-0BAD1DFA",
    "village": {
      "slug": "govtech",
      "name": "GovTech Village",
      "hall": "Hall A"
    },
    "companyName": "Selcom Paytech Tanzania Ltd",
    "boothPackage": "Premium Double Booth (6m x 3m)",
    "status": "PENDING_REVIEW",
    "createdAt": "2026-08-28T14:43:06.459948Z"
  }
}
```

**Response `400`** — Validation error (e.g. village slug not found for event).

```json
{
  "selected_village": "Village not found for this event."
}
```

---

## Error Responses

All endpoints return standard DRF error format for validation failures:

**`400 Bad Request`**

```json
{
  "field_name": ["This field is required."],
  "email": ["Enter a valid email address."]
}
```

**`404 Not Found`** — Event year not found or event not published.

```json
{
  "detail": "Not found."
}
```
