# Tanzania DPI Expo — Event Management API Architecture

## 1. Overview & Objectives

The **SLA Events API** provides a backend service to power yearly editions of the **Tanzania DPI Expo** and related conferences. 

Every event year (e.g. `2026`, `2027`) is a distinct database record with its own:
- **Hero & General Event Details** (Date, venue coordinates, slideshow photos, quick statistics)
- **Speakers & Keynotes**
- **Main Schedule & Sessions** (Keynotes, panel discussions, breakout workshops)
- **Specialized Expo Villages** (`GovTech`, `FinTech`, `Youth Innovation Hub`, `HealthTech`, `AgriTech`)
- **Dedicated Village Booths & Live Demo Timetables**
- **Historical & Showcase Photo Galleries**
- **Multi-Track Registration System** (Guests/Delegates, Dedicated Village Booth Applications, Speakers, Volunteers)

---

## 2. High-Level Architecture

```
┌────────────────────────────────────────────────────────┐
│             Vue 3 Frontend (Vite + TS)                 │
│  - Landing Page (Hero, Marquee, Focus Areas, Partners) │
│  - Event Details (/event)                              │
│  - Village Showcase (/village/:slug)                   │
│  - Dedicated Multi-Track Registration (/register)      │
└───────────────────────────▲────────────────────────────┘
                            │ REST / JSON (JWT for Admin)
┌───────────────────────────▼────────────────────────────┐
│         SLA Events Backend API (Node.js / Express)     │
│  - Express / TypeScript / Zod Validation               │
│  - Prisma ORM / PostgreSQL                             │
│  - Cloudinary / S3 Image Storage Engine                │
│  - Email Notification Dispatcher (SES / Resend)        │
└───────────────────────────┬────────────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │ PostgreSQL 16 DB   │
                  └────────────────────┘
```

---

## 3. Comprehensive Database Schema

### `events`
| Column          | Type      | Description                                      |
|-----------------|-----------|--------------------------------------------------|
| `id`            | UUID      | Primary key                                      |
| `year`          | INTEGER   | Unique year identifier (e.g. 2026, 2027)         |
| `title`         | VARCHAR   | "Tanzania DPI Expo 2026"                         |
| `tagline`       | TEXT      | Subtitle tagline                                 |
| `description`   | TEXT      | Full background overview                         |
| `start_date`    | DATE      | e.g. 2026-11-18                                  |
| `end_date`      | DATE      | e.g. 2026-11-19                                  |
| `venue_name`    | VARCHAR   | "Diamond Jubilee Expo Center"                    |
| `venue_address` | TEXT      | Full street address                              |
| `venue_lat`     | FLOAT     | Latitude for Google Maps embed                   |
| `venue_lng`     | FLOAT     | Longitude for Google Maps embed                  |
| `hero_images`   | TEXT[]    | URLs for hero carousel crossfade                 |
| `is_active`     | BOOLEAN   | Currently active edition displayed on home page  |
| `is_published`  | BOOLEAN   | Draft vs published status                        |
| `created_at`    | TIMESTAMP | Timestamp created                                |
| `updated_at`    | TIMESTAMP | Timestamp updated                                |

---

### `expo_villages` (Thematic Zones)
| Column          | Type      | Description                                               |
|-----------------|-----------|-----------------------------------------------------------|
| `id`            | UUID      | Primary key                                               |
| `event_id`      | UUID FK   | Links to `events`                                         |
| `slug`          | VARCHAR   | URL identifier (`govtech`, `fintech`, `youth`, etc.)      |
| `name`          | VARCHAR   | e.g. "GovTech Village", "FinTech Village"                 |
| `hall`          | VARCHAR   | Hall assignment (e.g. "Hall A — Main Exhibition Centre")  |
| `emoji`         | VARCHAR   | e.g. "🏛️", "💳", "🚀", "🏥", "🌾"                        |
| `theme_color`   | VARCHAR   | Hex accent (e.g. `#2563EB`, `#16A34A`, `#7C3AED`)         |
| `tagline`       | TEXT      | Catchphrase for the village                               |
| `description`   | TEXT      | Deep dive into village focus & public value               |
| `hero_image`    | TEXT      | Banner photography for village detail view                |
| `stats`         | JSONB     | Array of quick stats: `[{"label":"Booths","value":"14+"}]`|
| `order`         | INTEGER   | Sorting order in endless marquee and subnav               |

---

### `village_booths` (Exhibitors & Stands inside Villages)
| Column          | Type      | Description                                               |
|-----------------|-----------|-----------------------------------------------------------|
| `id`            | UUID      | Primary key                                               |
| `village_id`    | UUID FK   | Links to `expo_villages`                                  |
| `event_id`      | UUID FK   | Links to `events`                                         |
| `name`          | VARCHAR   | Stand / Showcase name (e.g. "GovNet & e-GA Gateway")      |
| `org`           | VARCHAR   | Exhibiting company or ministry                            |
| `booth_number`  | VARCHAR   | Stand code (e.g. "A-01", "B-05")                          |
| `tag`           | VARCHAR   | Category pill (e.g. "Infrastructure", "Identity", "GIS")  |
| `description`   | TEXT      | What is being presented at this booth                     |
| `live_demo`     | TEXT      | Time and title of interactive demo                        |
| `website_url`   | TEXT      | Exhibitor official URL                                    |
| `logo_url`      | TEXT      | High-resolution logo                                      |
| `is_featured`   | BOOLEAN   | Highlighted on village overview                           |
| `order`         | INTEGER   | Display priority                                          |

---

### `village_schedules` (Live Village Demo Timetable)
| Column          | Type      | Description                                               |
|-----------------|-----------|-----------------------------------------------------------|
| `id`            | UUID      | Primary key                                               |
| `village_id`    | UUID FK   | Links to `expo_villages`                                  |
| `time`          | VARCHAR   | Formatted time (e.g. "10:30 AM", "02:00 PM")              |
| `title`         | VARCHAR   | Session/Demo title                                        |
| `presenter`     | VARCHAR   | Name & Title of presenter                                 |
| `booth_or_stage`| VARCHAR   | Stage code or booth ID (e.g. "Stage A", "Lab 1", "A-04")  |
| `day_number`    | INTEGER   | Day 1 or Day 2                                            |
| `order`         | INTEGER   | Chronological sort                                        |

---

### `village_galleries` (Historical & Showcase Photo Stream)
| Column          | Type      | Description                                               |
|-----------------|-----------|-----------------------------------------------------------|
| `id`            | UUID      | Primary key                                               |
| `village_id`    | UUID FK   | Links to `expo_villages`                                  |
| `url`           | TEXT      | High-res photo URL                                        |
| `title`         | VARCHAR   | Caption title (e.g. "Citizen Portal Showcase")            |
| `caption`       | TEXT      | Detailed description of activity in picture               |
| `edition_year`  | INTEGER   | Year photo was taken (e.g. 2025, 2026)                    |
| `order`         | INTEGER   | Display sequence                                          |

---

### `booth_applications` (Dedicated Village Booth Registrations)
| Column               | Type      | Description                                                 |
|----------------------|-----------|-------------------------------------------------------------|
| `id`                 | UUID      | Primary key                                                 |
| `event_id`           | UUID FK   | Links to `events`                                           |
| `village_id`         | UUID FK   | Selected target Expo Village                                |
| `company_name`       | VARCHAR   | Legal company / organization name                           |
| `company_website`    | TEXT      | Official company URL                                        |
| `company_sector`     | VARCHAR   | Industry category                                           |
| `booth_package`      | VARCHAR   | `Shell Scheme (3x3)`, `Double Booth (6x3)`, `Startup Pod`, `Raw Space` |
| `showcase_title`     | VARCHAR   | Name of platform/solution to demonstrate                   |
| `showcase_desc`      | TEXT      | Interactive experience summary                              |
| `tech_requirements`  | TEXT[]    | Array of chosen add-ons (LAN, 4K Screen, 240V, Stage Slot)  |
| `co_exhibitors`      | TEXT      | Partner entities sharing booth space                        |
| `contact_first_name` | VARCHAR   | Lead coordinator first name                                 |
| `contact_last_name`  | VARCHAR   | Lead coordinator last name                                  |
| `contact_email`      | VARCHAR   | Work email address                                          |
| `contact_phone`      | VARCHAR   | Phone / WhatsApp                                            |
| `contact_job_title`  | VARCHAR   | Position in organization                                    |
| `country`            | VARCHAR   | Country of origin                                           |
| `status`             | ENUM      | `pending_review`, `approved`, `allocated`, `rejected`       |
| `assigned_booth_no`  | VARCHAR   | Assigned by expo floor manager (e.g. "B-04")                |
| `created_at`         | TIMESTAMP | Submission time                                             |

---

### `registrations` (General Delegates, Speakers & Volunteers)
| Column         | Type      | Description                                                 |
|----------------|-----------|-------------------------------------------------------------|
| `id`           | UUID      | Primary key                                                 |
| `event_id`     | UUID FK   | Links to `events`                                           |
| `type`         | ENUM      | `guest`, `speaker`, `volunteer`                             |
| `first_name`   | VARCHAR   | First name                                                  |
| `last_name`    | VARCHAR   | Last name                                                   |
| `email`        | VARCHAR   | Work / personal email                                       |
| `phone`        | VARCHAR   | Phone number                                                |
| `country`      | VARCHAR   | Country of residence                                        |
| `organization` | VARCHAR   | Organization name                                           |
| `extra_data`   | JSONB     | Type-specific fields (speaker bio, talk title, volunteer role, guest category) |
| `status`       | ENUM      | `confirmed`, `pending`, `waitlist`                          |
| `badge_code`   | VARCHAR   | Generated QR/Barcode code for on-site printing              |
| `created_at`   | TIMESTAMP |                                                             |

---

## 4. REST API Endpoint Specification

### Public Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/events/active` | Current active edition data for home page hero & stats |
| `GET` | `/api/events/:year` | Full event details by year (e.g. `2026`) |
| `GET` | `/api/events/:year/villages` | All 5 Expo Villages (for endless marquee & cards) |
| `GET` | `/api/events/:year/villages/:slug` | Specific village details by slug (`govtech`, `fintech`, etc.) |
| `GET` | `/api/events/:year/villages/:slug/booths` | Exhibitors & booths in the specified village |
| `GET` | `/api/events/:year/villages/:slug/schedule` | Live demonstration schedule for the village |
| `GET` | `/api/events/:year/villages/:slug/gallery` | Historical and current photo showcase gallery |
| `POST` | `/api/events/:year/register/booth` | **Dedicated Village Booth / Exhibitor Space Application** |
| `POST` | `/api/events/:year/register/guest` | Delegate & attendee badge registration |
| `POST` | `/api/events/:year/register/speaker` | Call for speakers application |
| `POST` | `/api/events/:year/register/volunteer` | Event crew / volunteer application |
| `GET` | `/api/events/:year/speakers` | List of confirmed keynote & panel speakers |
| `GET` | `/api/events/:year/schedule` | General conference schedule (Day 1 & Day 2) |
| `GET` | `/api/events/:year/partners` | Sponsors and organizing partners |

---

### Admin Endpoints (JWT Bearer Token Required)

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Admin authentication → returns JWT token |
| `POST` | `/api/admin/events` | Create a new event edition year |
| `PUT` | `/api/admin/events/:id/activate` | Toggle which year is the active live website |
| `POST` | `/api/admin/villages` | Create an Expo Village under an event |
| `PUT` | `/api/admin/villages/:id` | Update village description, theme color, or stats |
| `POST` | `/api/admin/villages/:id/booths` | Add / approve an exhibitor stand |
| `POST` | `/api/admin/villages/:id/schedule` | Add a demo session to the village timetable |
| `POST` | `/api/admin/villages/:id/gallery` | Upload photo highlights to the village gallery |
| `GET` | `/api/admin/booths/applications` | Review & approve pending village booth applications |
| `PUT` | `/api/admin/booths/applications/:id/status` | Update application status (`approved`, `allocated`, etc.) |
| `GET` | `/api/admin/registrations` | Export attendee & badge lists to CSV/Excel |

---

## 5. Sample Payloads

### A. Dedicated Booth Registration Request

`POST /api/events/2026/register/booth`

```json
{
  "selectedVillage": "govtech",
  "companyName": "Selcom Paytech Tanzania Ltd",
  "companyWebsite": "https://selcom.net",
  "companySector": "Fintech & Digital Payments",
  "boothPackage": "Premium Double Booth (6m x 3m)",
  "showcaseTitle": "Interoperable Micro-Merchant Payment QR Stack",
  "showcaseDescription": "Live point-of-sale checkout simulations demonstrating instant settlement across 8 banking switches and USSD offline channels.",
  "techRequirements": [
    "Dedicated High-Speed Wired LAN Connection (50 Mbps)",
    "55\" 4K Smart Display Screen with Floor Stand",
    "15-Minute Live Demo Slot on Village Stage"
  ],
  "coExhibitors": "In partnership with Bank of Tanzania (BoT)",
  "contact": {
    "firstName": "Amina",
    "lastName": "Kimaro",
    "email": "amina.kimaro@selcom.net",
    "phone": "+255712345678",
    "jobTitle": "Head of Partnerships & Digital Infrastructure",
    "country": "Tanzania"
  },
  "agreeTerms": true
}
```

#### Success Response (`201 Created`):
```json
{
  "success": true,
  "referenceNo": "TZ-DPI-BOOTH-849201",
  "message": "Your booth application for GovTech Village has been received.",
  "application": {
    "id": "c71a39f0-...",
    "village": "GovTech Village",
    "company": "Selcom Paytech Tanzania Ltd",
    "status": "pending_review"
  }
}
```

---

### B. Single Village Detail Response

`GET /api/events/2026/villages/govtech`

```json
{
  "id": "7b82e210-...",
  "slug": "govtech",
  "name": "GovTech Village",
  "hall": "Hall A — Main Exhibition Centre",
  "emoji": "🏛️",
  "themeColor": "#2563EB",
  "tagline": "Transforming Public Services Through Open Digital Infrastructure",
  "description": "Explore live, production-grade demonstrations of Tanzania’s next-generation e-Government platforms...",
  "heroImage": "https://images.unsplash.com/photo-1540575467063-178a50c2df87",
  "stats": [
    { "label": "Participating Agencies", "value": "14+" },
    { "label": "Live Digital Services", "value": "28" },
    { "label": "Interactive Demos", "value": "8/day" },
    { "label": "Capacity", "value": "350 Pax" }
  ],
  "boothsCount": 4,
  "booths": [
    {
      "id": "b1-...",
      "name": "GovNet & e-GA Gateway",
      "org": "e-Government Authority (eGA)",
      "boothNo": "A-01",
      "tag": "Infrastructure",
      "desc": "Interoperability middleware connecting 100+ ministries.",
      "liveDemo": "10:30 AM — Live Inter-agency Data Exchange"
    }
  ],
  "schedule": [
    {
      "time": "09:30 AM",
      "title": "Open-Source Public Digital Stack Architecture",
      "presenter": "Eng. Baraka Mtalo (eGA)",
      "booth": "Stage A"
    }
  ],
  "gallery": [
    {
      "url": "https://images.unsplash.com/photo-1531482615713-2afd69097998",
      "title": "Citizen Portal Showcase",
      "caption": "Demonstrating one-stop government service access"
    }
  ]
}
```

---

## 6. Prisma ORM Starter Schema (`prisma/schema.prisma`)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

enum RegType {
  GUEST
  BOOTH
  SPEAKER
  VOLUNTEER
}

enum AppStatus {
  PENDING_REVIEW
  APPROVED
  ALLOCATED
  REJECTED
}

model Event {
  id           String         @id @default(uuid())
  year         Int            @unique
  title        String
  tagline      String
  description  String?
  startDate    DateTime
  endDate      DateTime
  venueName    String
  venueAddress String
  venueLat     Float?
  venueLng     Float?
  heroImages   String[]
  isActive     Boolean        @default(false)
  isPublished  Boolean        @default(false)
  createdAt    DateTime       @default(now())
  updatedAt    DateTime       @updatedAt

  villages     ExpoVillage[]
  boothApps    BoothApplication[]
  speakers     Speaker[]
  sessions     Session[]
}

model ExpoVillage {
  id          String             @id @default(uuid())
  eventId     String
  event       Event              @relation(fields: [eventId], references: [id], onDelete: Cascade)
  slug        String
  name        String
  hall        String
  emoji       String
  themeColor  String
  tagline     String
  description String
  heroImage   String
  stats       Json
  order       Int                @default(0)

  booths      VillageBooth[]
  schedules   VillageSchedule[]
  galleries   VillageGallery[]
  boothApps   BoothApplication[]

  @@unique([eventId, slug])
}

model VillageBooth {
  id          String       @id @default(uuid())
  villageId   String
  village     ExpoVillage  @relation(fields: [villageId], references: [id], onDelete: Cascade)
  name        String
  org         String
  boothNumber String
  tag         String
  description String
  liveDemo    String?
  websiteUrl  String?
  logoUrl     String?
  isFeatured  Boolean      @default(false)
  order       Int          @default(0)
}

model VillageSchedule {
  id           String       @id @default(uuid())
  villageId    String
  village      ExpoVillage  @relation(fields: [villageId], references: [id], onDelete: Cascade)
  time         String
  title        String
  presenter    String
  boothOrStage String
  dayNumber    Int          @default(1)
  order        Int          @default(0)
}

model VillageGallery {
  id          String       @id @default(uuid())
  villageId   String
  village     ExpoVillage  @relation(fields: [villageId], references: [id], onDelete: Cascade)
  url         String
  title       String
  caption     String
  editionYear Int
  order       Int          @default(0)
}

model BoothApplication {
  id               String       @id @default(uuid())
  eventId          String
  event            Event        @relation(fields: [eventId], references: [id])
  villageId        String
  village          ExpoVillage  @relation(fields: [villageId], references: [id])
  companyName      String
  companyWebsite   String?
  companySector    String?
  boothPackage     String
  showcaseTitle    String
  showcaseDesc     String
  techRequirements String[]
  coExhibitors     String?
  firstName        String
  lastName         String
  email            String
  phone            String
  jobTitle         String?
  country          String
  status           AppStatus    @default(PENDING_REVIEW)
  assignedBoothNo  String?
  createdAt        DateTime     @default(now())
}

model Speaker {
  id          String    @id @default(uuid())
  eventId     String
  event       Event     @relation(fields: [eventId], references: [id], onDelete: Cascade)
  name        String
  title       String
  org         String
  bio         String?
  photoUrl    String?
  order       Int       @default(0)
  isConfirmed Boolean   @default(true)
}

model Session {
  id        String    @id @default(uuid())
  eventId   String
  event     Event     @relation(fields: [eventId], references: [id], onDelete: Cascade)
  dayNumber Int
  startTime String
  endTime   String
  title     String
  type      String
  speaker   String?
  location  String?
}
```

---

## 7. Implementation Roadmap

1. **Scaffold the API Repo (`sla-events-api`)**:
   - `npm init -y` with TypeScript, Express, Prisma, Zod, and Cors.
2. **Apply Database Migrations**:
   - Run `npx prisma migrate dev --name init_events_and_villages`.
   - Seed `2026` event data with the 5 Expo Villages, sample booths, and schedules.
3. **Deploy Core Endpoints**:
   - `GET /api/events/active`
   - `GET /api/events/:year/villages/:slug`
   - `POST /api/events/:year/register/booth`
4. **Connect Frontend**:
   - Configure `VITE_API_URL` in `.env`.
   - Create `src/composables/useVillages.ts` and `src/composables/useRegistration.ts` to replace local static mock data.
