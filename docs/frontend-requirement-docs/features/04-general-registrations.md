# Feature 04: General Registrations (Guests, Speakers, Volunteers)

## 1. Overview
Handles attendee registrations for:
1. **Guests & Delegates** (General admission, policymaker, developer, researcher passes)
2. **Call for Speakers** (Abstract submission, speaker biography, previous stage appearances)
3. **Volunteers** (Event crew roles, shift availability slots, skill sets)

---

## 2. Database Schema & Tables

### 2.1 Table: `registrations`
Stores all general attendee registrations, call for speaker proposals, and volunteer submissions.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique registration ID |
| `reference_no` | VARCHAR(50) | NOT NULL, UNIQUE | Reference code (e.g. `TZ-DPI-GUEST-719283`) |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` | Event edition |
| `type` | ENUM | NOT NULL | `GUEST`, `SPEAKER`, `VOLUNTEER` |
| `first_name` | VARCHAR(100) | NOT NULL | Attendee first name |
| `last_name` | VARCHAR(100) | NOT NULL | Attendee last name |
| `email` | VARCHAR(255) | NOT NULL | Email address |
| `phone` | VARCHAR(50) | NOT NULL | Phone number |
| `country` | VARCHAR(100) | NOT NULL | Country of residence |
| `organization` | VARCHAR(200) | NULLABLE | Organization / Institution |
| `extra_data` | JSONB | NOT NULL, DEFAULT `{}` | Type-specific payload (guest category, talk abstract, shifts) |
| `status` | ENUM | NOT NULL, DEFAULT `'CONFIRMED'` | `CONFIRMED`, `PENDING_REVIEW`, `APPROVED`, `WAITLIST`, `REJECTED` |
| `badge_code` | VARCHAR(100) | NOT NULL, UNIQUE | Unique string for barcode/QR generation |
| `agree_terms` | BOOLEAN | NOT NULL, DEFAULT `true` | Terms acceptance |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Submission timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Update timestamp |

*Unique Constraint*: `UNIQUE (event_id, email, type)`

### 2.2 Prisma Model
```prisma
enum RegistrationType {
  GUEST
  SPEAKER
  VOLUNTEER
}

enum RegStatus {
  CONFIRMED
  PENDING_REVIEW
  APPROVED
  WAITLIST
  REJECTED
}

model Registration {
  id           String           @id @default(uuid())
  referenceNo  String           @unique @map("reference_no")
  eventId      String           @map("event_id")
  event        Event            @relation(fields: [eventId], references: [id], onDelete: Cascade)
  type         RegistrationType
  firstName    String           @map("first_name")
  lastName     String           @map("last_name")
  email        String
  phone        String
  country      String
  organization String?
  extraData    Json             @default("{}") @map("extra_data")
  status       RegStatus        @default(CONFIRMED)
  badgeCode    String           @unique @map("badge_code")
  agreeTerms   Boolean          @default(true) @map("agree_terms")
  createdAt    DateTime         @default(now()) @map("created_at")
  updatedAt    DateTime         @updatedAt @map("updated_at")

  @@unique([eventId, email, type])
  @@map("registrations")
}
```

---

## 3. API Endpoints

### 3.1 Submit Guest / Delegate Registration
- **Method**: `POST`
- **Path**: `/api/events/:year/register/guest`
- **Auth**: None (Public)

#### Request Payload
```json
{
  "firstName": "John",
  "lastName": "Kamau",
  "email": "john.kamau@example.org",
  "phone": "+255712987654",
  "country": "Tanzania",
  "organization": "e-Government Authority",
  "guestCategory": "Policymaker / Government Official",
  "dietaryReqs": "Vegetarian",
  "agreeTerms": true
}
```

#### Response `201 Created`
```json
{
  "success": true,
  "referenceNo": "TZ-DPI-GUEST-719283",
  "badgeCode": "QR-719283-EGA",
  "message": "Registration confirmed. Entry badge sent to your email.",
  "data": {
    "id": "e91a02b1-...",
    "type": "GUEST",
    "name": "John Kamau",
    "email": "john.kamau@example.org",
    "status": "CONFIRMED"
  }
}
```

---

### 3.2 Submit Speaker Proposal
- **Method**: `POST`
- **Path**: `/api/events/:year/register/speaker`
- **Auth**: None (Public)

#### Request Payload
```json
{
  "firstName": "Dr. Fatma",
  "lastName": "Hassan",
  "email": "dr.fatma@ict.go.tz",
  "phone": "+255788112233",
  "country": "Tanzania",
  "organization": "Ministry of ICT",
  "talkTitle": "Building Africa's Interoperable Public Digital Foundation",
  "talkAbstract": "A 45-minute keynote examining sovereign digital identity and cross-border instant payment interoperability.",
  "speakerBio": "Minister of ICT with over 15 years leading telecommunication policy and national infrastructure initiatives.",
  "linkedIn": "https://linkedin.com/in/drfatmahassan",
  "previousSpeaking": "GSMA Mobile 360, World Bank DPI Summit",
  "agreeTerms": true
}
```

---

### 3.3 Submit Volunteer Application
- **Method**: `POST`
- **Path**: `/api/events/:year/register/volunteer`
- **Auth**: None (Public)

#### Request Payload
```json
{
  "firstName": "Grace",
  "lastName": "Massawe",
  "email": "grace.massawe@udsm.ac.tz",
  "phone": "+255755443322",
  "country": "Tanzania",
  "organization": "University of Dar es Salaam",
  "volunteerRole": "Exhibition Floor Support",
  "availability": [
    "Day 1 Morning (Nov 18, 08:00 – 13:00)",
    "Day 1 Afternoon (Nov 18, 13:00 – 18:00)",
    "Day 2 Morning (Nov 19, 08:00 – 13:00)"
  ],
  "skills": "Bilingual (English/Swahili), IT Support, Registration Software",
  "motivation": "Passionate about open technology and eager to assist regional delegates.",
  "agreeTerms": true
}
```
