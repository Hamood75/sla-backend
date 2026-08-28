# Feature 02: Expo Villages (Thematic Exhibition Zones)

## 1. Overview
Expo Villages are the 5 core thematic zones (`GovTech`, `FinTech`, `Youth Innovation Hub`, `HealthTech`, `AgriTech`). Each village has dedicated hall locations, branding colors, emojis, stats, and a list of live showcases.

---

## 2. Database Schema & Tables

### 2.1 Table: `expo_villages`
Stores the thematic zone metadata, hall assignments, and styling parameters.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique village identifier |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` ON DELETE CASCADE | Associated event edition |
| `slug` | VARCHAR(50) | NOT NULL | URL identifier (`govtech`, `fintech`, `youth`, `healthtech`, `agritech`) |
| `name` | VARCHAR(150) | NOT NULL | Display name (e.g. "GovTech Village") |
| `hall` | VARCHAR(150) | NOT NULL | Hall & building (e.g. "Hall A — Main Exhibition Centre") |
| `emoji` | VARCHAR(20) | NOT NULL | Visual emoji/icon (e.g. "🏛️", "💳", "🚀", "🏥", "🌾") |
| `theme_color` | VARCHAR(30) | NOT NULL | Accent hex color (e.g. `#2563EB`, `#16A34A`) |
| `tagline` | TEXT | NOT NULL | Short catchphrase |
| `description` | TEXT | NOT NULL | In-depth description of village scope |
| `hero_image` | TEXT | NOT NULL | Banner photography URL |
| `stats` | JSONB | NOT NULL, DEFAULT `[]` | Array of stats: `[{"label":"Booths","value":"14+"}]` |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Order in marquee and switcher pills |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Update timestamp |

*Unique Constraint*: `UNIQUE (event_id, slug)`

### 2.2 Table: `village_booths`
Stores the participating exhibitors, ministries, and companies within each village.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique stand identifier |
| `village_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `expo_villages(id)` ON DELETE CASCADE | Assigned village |
| `name` | VARCHAR(200) | NOT NULL | Stand title (e.g. "GovNet & e-GA Gateway") |
| `org` | VARCHAR(200) | NOT NULL | Exhibiting entity / ministry |
| `booth_number` | VARCHAR(50) | NOT NULL | Stand allocation code (e.g. "A-01", "B-05") |
| `tag` | VARCHAR(50) | NOT NULL | Category pill (e.g. "Infrastructure", "Payments") |
| `description` | TEXT | NOT NULL | Summary of what is showcased |
| `live_demo` | TEXT | NULLABLE | Demo time and focus topic |
| `website_url` | TEXT | NULLABLE | Link to exhibitor website |
| `logo_url` | TEXT | NULLABLE | Company logo URL |
| `is_featured` | BOOLEAN | NOT NULL, DEFAULT `false` | Highlighted stand toggle |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Sequence priority |

### 2.3 Table: `village_schedules`
Stores the daily timetable of stage demonstrations and workshops running in this village.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique schedule item ID |
| `village_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `expo_villages(id)` ON DELETE CASCADE | Assigned village |
| `time` | VARCHAR(50) | NOT NULL | Formatted time (e.g. "09:30 AM", "02:00 PM") |
| `title` | VARCHAR(255) | NOT NULL | Title of presentation / live demo |
| `presenter` | VARCHAR(200) | NOT NULL | Speaker name and organization |
| `booth_or_stage` | VARCHAR(100) | NOT NULL | Location code (e.g. "Stage A", "A-04", "Lab 1") |
| `day_number` | INTEGER | NOT NULL, DEFAULT `1` | 1 or 2 |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Chronological sorting order |

### 2.4 Table: `village_galleries`
Stores previous and current edition photography for this village.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique photo ID |
| `village_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `expo_villages(id)` ON DELETE CASCADE | Assigned village |
| `url` | TEXT | NOT NULL | High-resolution image URL |
| `title` | VARCHAR(200) | NOT NULL | Caption header |
| `caption` | TEXT | NOT NULL | Detailed photo caption |
| `edition_year` | INTEGER | NOT NULL, DEFAULT `2026` | Year photo was captured |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Sequence in gallery grid |

### 2.5 Prisma Models
```prisma
model ExpoVillage {
  id          String            @id @default(uuid())
  eventId     String            @map("event_id")
  event       Event             @relation(fields: [eventId], references: [id], onDelete: Cascade)
  slug        String
  name        String
  hall        String
  emoji       String
  themeColor  String            @map("theme_color")
  tagline     String
  description String
  heroImage   String            @map("hero_image")
  stats       Json              @default("[]")
  order       Int               @default(0)
  createdAt   DateTime          @default(now()) @map("created_at")
  updatedAt   DateTime          @updatedAt @map("updated_at")

  booths      VillageBooth[]
  schedules   VillageSchedule[]
  galleries   VillageGallery[]
  boothApps   BoothApplication[]

  @@unique([eventId, slug])
  @@map("expo_villages")
}

model VillageBooth {
  id          String      @id @default(uuid())
  villageId   String      @map("village_id")
  village     ExpoVillage @relation(fields: [villageId], references: [id], onDelete: Cascade)
  name        String
  org         String
  boothNumber String      @map("booth_number")
  tag         String
  description String
  liveDemo    String?     @map("live_demo")
  websiteUrl  String?     @map("website_url")
  logoUrl     String?     @map("logo_url")
  isFeatured  Boolean     @default(false) @map("is_featured")
  order       Int         @default(0)

  @@map("village_booths")
}

model VillageSchedule {
  id           String      @id @default(uuid())
  villageId    String      @map("village_id")
  village      ExpoVillage @relation(fields: [villageId], references: [id], onDelete: Cascade)
  time         String
  title        String
  presenter    String
  boothOrStage String      @map("booth_or_stage")
  dayNumber    Int         @default(1) @map("day_number")
  order        Int         @default(0)

  @@map("village_schedules")
}

model VillageGallery {
  id          String      @id @default(uuid())
  villageId   String      @map("village_id")
  village     ExpoVillage @relation(fields: [villageId], references: [id], onDelete: Cascade)
  url         String
  title       String
  caption     String
  editionYear Int         @default(2026) @map("edition_year")
  order       Int         @default(0)

  @@map("village_galleries")
}
```

---

## 3. API Endpoints

### 3.1 List All Villages for an Event
Powers the home page endless scrolling marquee and the village navigation pills.

- **Method**: `GET`
- **Path**: `/api/events/:year/villages`
- **Auth**: None (Public)

#### Response `200 OK`
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": "7b82e210-91ab-4d43-98fe-08c37d6e4210",
      "slug": "govtech",
      "name": "GovTech Village",
      "hall": "Hall A",
      "emoji": "🏛️",
      "themeColor": "#2563EB",
      "tagline": "Transforming Public Services Through Open Digital Infrastructure",
      "desc": "Live demos of e-Government platforms, digital ID, land registries, and citizen service portals from Tanzania's leading public institutions.",
      "heroImage": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1800&auto=format&fit=crop&q=80",
      "boothsCount": 14,
      "demosCount": 8,
      "order": 1
    }
  ]
}
```

---

### 3.2 Get Specific Village Details by Slug
Powers the `/village/:slug` page with full aggregated booth list, demo schedule, and showcase gallery.

- **Method**: `GET`
- **Path**: `/api/events/:year/villages/:slug`
- **Auth**: None (Public)

#### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "7b82e210-91ab-4d43-98fe-08c37d6e4210",
    "slug": "govtech",
    "name": "GovTech Village",
    "hall": "Hall A — Main Exhibition Centre",
    "emoji": "🏛️",
    "themeColor": "#2563EB",
    "tagline": "Transforming Public Services Through Open Digital Infrastructure",
    "description": "Explore live, production-grade demonstrations of Tanzania’s next-generation e-Government platforms...",
    "heroImage": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1800&auto=format&fit=crop&q=80",
    "stats": [
      { "label": "Participating Agencies", "value": "14+" },
      { "label": "Live Digital Services", "value": "28" },
      { "label": "Interactive Demos", "value": "8/day" },
      { "label": "Capacity", "value": "350 Pax" }
    ],
    "booths": [
      {
        "id": "b1-91a",
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
        "id": "s1-02a",
        "time": "09:30 AM",
        "title": "Open-Source Public Digital Stack Architecture",
        "presenter": "Eng. Baraka Mtalo (eGA)",
        "booth": "Stage A"
      }
    ],
    "gallery": [
      {
        "id": "g1-01a",
        "url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&auto=format&fit=crop&q=80",
        "title": "Citizen Portal Showcase",
        "caption": "Demonstrating one-stop government service access"
      }
    ]
  }
}
```
