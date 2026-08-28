# Feature 05: Speakers & Program Schedule

## 1. Overview
Manages the main conference schedule across multiple days (`Day 1`, `Day 2`), linking keynotes and panel sessions to confirmed speakers and stages.

---

## 2. Database Schema & Tables

### 2.1 Table: `speakers`
Stores verified keynote and panel speakers.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique speaker ID |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` ON DELETE CASCADE | Associated event edition |
| `name` | VARCHAR(150) | NOT NULL | Full name with title (e.g. "Dr. Fatma Hassan") |
| `title` | VARCHAR(150) | NOT NULL | Professional designation (e.g. "Minister of ICT") |
| `org` | VARCHAR(200) | NOT NULL | Organization / Government Body |
| `initials` | VARCHAR(10) | NOT NULL | Fallback avatar initials (e.g. "FH") |
| `color` | VARCHAR(30) | NOT NULL | Brand accent color (e.g. `#1E40AF`) |
| `accent_light` | VARCHAR(30) | NOT NULL | Subtle background tint (e.g. `#DBEAFE`) |
| `photo_url` | TEXT | NOT NULL | Profile portrait URL |
| `bio` | TEXT | NULLABLE | Full biography |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Display order sequence |
| `is_confirmed` | BOOLEAN | NOT NULL, DEFAULT `true` | Visibility toggle |

### 2.2 Table: `sessions`
Stores conference sessions, opening ceremonies, keynotes, panel discussions, and workshop tracks.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique session ID |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` ON DELETE CASCADE | Associated event edition |
| `day_number` | INTEGER | NOT NULL, DEFAULT `1` | Day 1 or Day 2 |
| `start_time` | VARCHAR(20) | NOT NULL | Start time (e.g. "09:00") |
| `end_time` | VARCHAR(20) | NOT NULL | End time (e.g. "10:30") |
| `title` | VARCHAR(255) | NOT NULL | Session topic |
| `type` | ENUM | NOT NULL | `KEYNOTE`, `PANEL`, `WORKSHOP`, `BREAK`, `EXHIBITION` |
| `speaker_id` | UUID | NULLABLE, FOREIGN KEY REFERENCES `speakers(id)` | Linked speaker (if solo) |
| `speaker_text` | VARCHAR(200) | NULLABLE | Free text speaker/panelist string |
| `location` | VARCHAR(150) | NOT NULL | Stage or room (e.g. "Auditorium A") |
| `order` | INTEGER | NOT NULL, DEFAULT `0` | Sequence |

### 2.3 Prisma Models
```prisma
enum SessionType {
  KEYNOTE
  PANEL
  WORKSHOP
  BREAK
  EXHIBITION
}

model Speaker {
  id          String    @id @default(uuid())
  eventId     String    @map("event_id")
  event       Event     @relation(fields: [eventId], references: [id], onDelete: Cascade)
  name        String
  title       String
  org         String
  initials    String
  color       String
  accentLight String    @map("accent_light")
  photoUrl    String    @map("photo_url")
  bio         String?
  order       Int       @default(0)
  isConfirmed Boolean   @default(true) @map("is_confirmed")

  sessions    Session[]

  @@map("speakers")
}

model Session {
  id          String      @id @default(uuid())
  eventId     String      @map("event_id")
  event       Event       @relation(fields: [eventId], references: [id], onDelete: Cascade)
  dayNumber   Int         @map("day_number")
  startTime   String      @map("start_time")
  endTime     String      @map("end_time")
  title       String
  type        SessionType
  speakerId   String?     @map("speaker_id")
  speakerRel  Speaker?    @relation(fields: [speakerId], references: [id])
  speakerText String?     @map("speaker_text")
  location    String
  order       Int         @default(0)

  @@map("sessions")
}
```

---

## 3. API Endpoints

### 3.1 Get Confirmed Speakers
- **Method**: `GET`
- **Path**: `/api/events/:year/speakers`
- **Auth**: None (Public)

#### Response `200 OK`
```json
{
  "success": true,
  "count": 6,
  "data": [
    {
      "id": "spk-01",
      "name": "Dr. Fatma Hassan",
      "title": "Minister of ICT",
      "org": "Government of Tanzania",
      "initials": "FH",
      "color": "#1E40AF",
      "accentLight": "#DBEAFE",
      "photo": "https://randomuser.me/api/portraits/women/44.jpg",
      "bio": "Leading national telecommunication transformation and sovereign digital stack policies.",
      "order": 1
    }
  ]
}
```

---

### 3.2 Get Conference Schedule
- **Method**: `GET`
- **Path**: `/api/events/:year/schedule`
- **Auth**: None (Public)

#### Response `200 OK`
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
          "id": "sess-01",
          "time": "08:00 – 09:00",
          "title": "Registration & Welcome Coffee",
          "type": "BREAK",
          "location": "Main Foyer"
        },
        {
          "id": "sess-02",
          "time": "09:00 – 09:30",
          "title": "Official Opening Ceremony",
          "speaker": "Minister of ICT",
          "type": "KEYNOTE",
          "location": "Auditorium A"
        }
      ]
    }
  ]
}
```
