# Feature 01: Events Management & Full Landing Page API

## 1. Overview
The Events Management feature handles multi-year conference editions (`2026`, `2027`) and serves the **complete, aggregated landing page payload** in a single optimized request (`GET /api/events/landing` or `GET /api/events/active`).

This powers the entire `HomePage.vue` without requiring cascading API calls:
1. **Hero Banner & Slideshow** (crossfade photos, dates, countdown, GPS venue)
2. **Key Metrics / Stats Bar** (Days, Speakers, Exhibitors, Attendees, Countries)
3. **Endless Expo Village Marquee** (5 thematic zones with live demo & booth counters)
4. **Showcase Gallery Strip** (Photo highlights from previous editions)
5. **Focus Areas Carousel** (DPI thematic tracks, icons, accent colors)
6. **Partners & Sponsors Strip** (Government ministries, international agencies, innovators)
7. **Featured Speakers Preview** (Keynote leaders)

---

## 2. Database Schema & Tables

### 2.1 Table: `events`
Stores core metadata, dates, venue coordinates, and status for each yearly edition.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique event identifier |
| `year` | INTEGER | NOT NULL, UNIQUE | Edition year (e.g. `2026`, `2027`) |
| `title` | VARCHAR(255) | NOT NULL | Official event title ("Tanzania DPI Expo 2026") |
| `tagline` | TEXT | NOT NULL | Hero subtitle / theme statement |
| `description` | TEXT | NULLABLE | Detailed overview of the edition |
| `start_date` | TIMESTAMPTZ | NOT NULL | Event start date and time |
| `end_date` | TIMESTAMPTZ | NOT NULL | Event end date and time |
| `venue_name` | VARCHAR(255) | NOT NULL | Name of exhibition center ("Diamond Jubilee Expo Center") |
| `venue_address` | TEXT | NOT NULL | Full street address string |
| `venue_lat` | DOUBLE PRECISION | NULLABLE | GPS latitude (-6.8161) |
| `venue_lng` | DOUBLE PRECISION | NULLABLE | GPS longitude (39.2804) |
| `hero_images` | TEXT[] | NOT NULL, DEFAULT `{}` | Array of image URLs for hero slideshow crossfade |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `false` | True if this is the active edition on the website |
| `is_published` | BOOLEAN | NOT NULL, DEFAULT `false` | True if public, false if draft in admin |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Record update timestamp |

### 2.2 Table: `event_stats`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique stat identifier |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` ON DELETE CASCADE | Parent event edition |
| `label` | VARCHAR(100) | NOT NULL | Stat title ("Speakers", "Countries") |
| `value` | VARCHAR(50) | NOT NULL | Counter display ("50+", "15+") |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Display order sequence |

### 2.3 Table: `focus_areas`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique focus area ID |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` ON DELETE CASCADE | Parent event edition |
| `num` | VARCHAR(10) | NOT NULL | Order index ("01", "02", "03") |
| `title` | VARCHAR(150) | NOT NULL | Focus topic title |
| `description` | TEXT | NOT NULL | Summary text |
| `accent_color`| VARCHAR(30) | NOT NULL | Accent hex color (e.g. `#1E40AF`, `#F97316`) |
| `badge_color` | VARCHAR(30) | NOT NULL | Badge hex tint |
| `image_url`   | TEXT | NOT NULL | Card background photography |
| `order`       | INTEGER | NOT NULL, DEFAULT `0` | Sequence |

### 2.4 Table: `partners`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique partner ID |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` ON DELETE CASCADE | Parent event edition |
| `name` | VARCHAR(150) | NOT NULL | Organization / Partner name |
| `logo_url` | TEXT | NOT NULL | Logo image URL |
| `tier` | VARCHAR(50) | NOT NULL, DEFAULT `'PARTNER'` | `HOST`, `LEAD_PARTNER`, `PARTNER`, `MEDIA` |
| `website_url` | TEXT | NULLABLE | Partner official link |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Marquee display order |

### 2.5 Prisma Models
```prisma
model Event {
  id           String       @id @default(uuid())
  year         Int          @unique
  title        String
  tagline      String
  description  String?
  startDate    DateTime     @map("start_date")
  endDate      DateTime     @map("end_date")
  venueName    String       @map("venue_name")
  venueAddress String       @map("venue_address")
  venueLat     Float?       @map("venue_lat")
  venueLng     Float?       @map("venue_lng")
  heroImages   String[]     @default([]) @map("hero_images")
  isActive     Boolean      @default(false) @map("is_active")
  isPublished  Boolean      @default(false) @map("is_published")
  createdAt    DateTime     @default(now()) @map("created_at")
  updatedAt    DateTime     @updatedAt @map("updated_at")

  stats        EventStat[]
  focusAreas   FocusArea[]
  partners     Partner[]
  villages     ExpoVillage[]
  speakers     Speaker[]
  sessions     Session[]

  @@map("events")
}

model EventStat {
  id      String @id @default(uuid())
  eventId String @map("event_id")
  event   Event  @relation(fields: [eventId], references: [id], onDelete: Cascade)
  label   String
  value   String
  order   Int    @default(0)

  @@map("event_stats")
}

model FocusArea {
  id          String @id @default(uuid())
  eventId     String @map("event_id")
  event       Event  @relation(fields: [eventId], references: [id], onDelete: Cascade)
  num         String
  title       String
  description String
  accentColor String @map("accent_color")
  badgeColor  String @map("badge_color")
  imageUrl    String @map("image_url")
  order       Int    @default(0)

  @@map("focus_areas")
}

model Partner {
  id         String  @id @default(uuid())
  eventId    String  @map("event_id")
  event      Event   @relation(fields: [eventId], references: [id], onDelete: Cascade)
  name       String
  logoUrl    String  @map("logo_url")
  tier       String  @default("PARTNER")
  websiteUrl String? @map("website_url")
  order      Int     @default(0)

  @@map("partners")
}
```

---

## 3. API Endpoints

### 3.1 Get Full Landing Page Aggregate
Returns the complete payload required to render `HomePage.vue` in a single round-trip.

- **Method**: `GET`
- **Path**: `/api/events/landing` (or `/api/events/active`)
- **Auth**: None (Public)

#### Full JSON Response `200 OK`
```json
{
  "success": true,
  "data": {
    "event": {
      "id": "e8a93e80-7c22-49d6-9430-84a129188091",
      "year": 2026,
      "title": "Tanzania DPI Expo 2026",
      "tagline": "Building the Digital Foundation for an Inclusive Tanzania",
      "startDate": "2026-11-18T08:00:00.000Z",
      "endDate": "2026-11-19T18:00:00.000Z",
      "venue": {
        "name": "Diamond Jubilee Expo Center",
        "address": "Ohio Street (Kenyatta Drive), Dar es Salaam, Tanzania",
        "latitude": -6.8161,
        "longitude": 39.2804
      },
      "heroImages": [
        "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1551818255-e6e10975bc17?w=1800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=1800&auto=format&fit=crop&q=80"
      ]
    },

    "stats": [
      { "label": "Days", "value": "2" },
      { "label": "Speakers", "value": "50+" },
      { "label": "Exhibitors", "value": "30+" },
      { "label": "Attendees", "value": "10K+" },
      { "label": "Countries", "value": "15+" }
    ],

    "villages": [
      {
        "id": "govtech",
        "name": "GovTech Village",
        "hall": "Hall A",
        "emoji": "🏛️",
        "color": "#2563EB",
        "img": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80",
        "desc": "Live demos of e-Government platforms, digital ID, land registries, and citizen service portals from Tanzania's leading public institutions.",
        "booths": "14+",
        "demos": "8"
      },
      {
        "id": "fintech",
        "name": "FinTech Village",
        "hall": "Hall B",
        "emoji": "💳",
        "color": "#16A34A",
        "img": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&auto=format&fit=crop&q=80",
        "desc": "Hands-on experiences with mobile money innovations, digital banking, payment infrastructure, and financial inclusion tools.",
        "booths": "10+",
        "demos": "6"
      },
      {
        "id": "youth",
        "name": "Youth Innovation Hub",
        "hall": "Hall C",
        "emoji": "🚀",
        "color": "#7C3AED",
        "img": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&auto=format&fit=crop&q=80",
        "desc": "A dedicated stage for Tanzania's next generation of tech founders — pitching, demos, hackathon results, and live coding challenges.",
        "booths": "20+",
        "demos": "Pitch Stage"
      },
      {
        "id": "healthtech",
        "name": "HealthTech Village",
        "hall": "Hall D",
        "emoji": "🏥",
        "color": "#DC2626",
        "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&auto=format&fit=crop&q=80",
        "desc": "Showcasing digital health records, telemedicine platforms, community health workers' tools, and AI-powered diagnostics.",
        "booths": "8+",
        "demos": "5"
      },
      {
        "id": "agritech",
        "name": "AgriTech Village",
        "hall": "Hall E",
        "emoji": "🌾",
        "color": "#D97706",
        "img": "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=800&auto=format&fit=crop&q=80",
        "desc": "Digital tools for farmers, market linkage platforms, drone demonstrations, and smart irrigation systems transforming food security.",
        "booths": "10+",
        "demos": "4"
      }
    ],

    "gallery": [
      {
        "id": "gal-01",
        "url": "https://images.unsplash.com/photo-1567967455389-e432b2862a72?w=600&auto=format&fit=crop&q=80",
        "title": "Exhibition Floor",
        "layout": "tall"
      },
      {
        "id": "gal-02",
        "url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&auto=format&fit=crop&q=80",
        "title": "Keynote Stage",
        "layout": "standard"
      },
      {
        "id": "gal-03",
        "url": "https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=600&auto=format&fit=crop&q=80",
        "title": "Networking Zone",
        "layout": "standard"
      },
      {
        "id": "gal-04",
        "url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80",
        "title": "Hands-on Workshops",
        "layout": "wide"
      }
    ],

    "focusAreas": [
      {
        "num": "01",
        "title": "Keynote Addresses",
        "desc": "Inspiring talks from leaders driving the digital transformation agenda.",
        "accentColor": "#F97316",
        "badgeColor": "#EA580C",
        "img": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop&q=80"
      },
      {
        "num": "02",
        "title": "Exhibition & Showcase",
        "desc": "Explore cutting-edge solutions and digital innovations in 5 specialized villages.",
        "accentColor": "#002B7F",
        "badgeColor": "#002B7F",
        "img": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80"
      },
      {
        "num": "03",
        "title": "Expert Panels",
        "desc": "Engage in conversations shaping the future of African DPI.",
        "accentColor": "#F97316",
        "badgeColor": "#EA580C",
        "img": "https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=800&auto=format&fit=crop&q=80"
      },
      {
        "num": "04",
        "title": "Networking Opportunities",
        "desc": "Connect, collaborate and build public-private partnerships.",
        "accentColor": "#16A34A",
        "badgeColor": "#16A34A",
        "img": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80"
      },
      {
        "num": "05",
        "title": "Workshops & Masterclasses",
        "desc": "Learn, upskill and exchange practical open-source knowledge.",
        "accentColor": "#002B7F",
        "badgeColor": "#002B7F",
        "img": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&auto=format&fit=crop&q=80"
      }
    ],

    "partners": [
      { "name": "iDEA", "logo": "https://cdn.tanzaniadpiexpo.org/partners/idea.png" },
      { "name": "CTA", "logo": "https://cdn.tanzaniadpiexpo.org/partners/cta.png" },
      { "name": "Ministry of ICT", "logo": "https://cdn.tanzaniadpiexpo.org/partners/mict.png" },
      { "name": "Street Labs", "logo": "https://cdn.tanzaniadpiexpo.org/partners/streetlabs.png" },
      { "name": "eGA", "logo": "https://cdn.tanzaniadpiexpo.org/partners/ega.png" },
      { "name": "Government of Tanzania", "logo": "https://cdn.tanzaniadpiexpo.org/partners/got.png" }
    ],

    "featuredSpeakers": [
      {
        "name": "Dr. Fatma Hassan",
        "title": "Minister of ICT",
        "org": "Government of Tanzania",
        "photo": "https://randomuser.me/api/portraits/women/44.jpg"
      },
      {
        "name": "John Kamau",
        "title": "Director General",
        "org": "eGA East Africa",
        "photo": "https://randomuser.me/api/portraits/men/32.jpg"
      }
    ]
  }
}
```
