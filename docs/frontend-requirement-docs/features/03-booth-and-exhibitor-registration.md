# Feature 03: Dedicated Booth & Village Exhibitor Registration

## 1. Overview
The dedicated **Exhibitor / Booth Registration** feature allows companies, government agencies, and startups to apply for exhibition space in one of the 5 Expo Villages.

---

## 2. Database Schema & Tables

### 2.1 Table: `booth_applications`
Stores all exhibitor space applications, selected packages, technical needs, and administrative review status.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique application ID |
| `reference_no` | VARCHAR(50) | NOT NULL, UNIQUE | Public reference (e.g. `TZ-DPI-BOOTH-849201`) |
| `event_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `events(id)` | Associated event year |
| `village_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES `expo_villages(id)` | Selected Expo Village |
| `company_name` | VARCHAR(200) | NOT NULL | Legal organization name |
| `company_website` | TEXT | NULLABLE | Official website URL |
| `company_sector` | VARCHAR(100) | NULLABLE | Industry sector |
| `booth_package` | VARCHAR(100) | NOT NULL | Stand package selected |
| `showcase_title` | VARCHAR(255) | NOT NULL | Name of product/system to demo |
| `showcase_desc` | TEXT | NOT NULL | Demonstration interactivity details |
| `tech_requirements` | TEXT[] | NOT NULL, DEFAULT `{}` | Array of technical add-ons (LAN, 4K screen, demo slots) |
| `co_exhibitors` | TEXT | NULLABLE | Partners sharing booth |
| `first_name` | VARCHAR(100) | NOT NULL | Primary coordinator first name |
| `last_name` | VARCHAR(100) | NOT NULL | Primary coordinator last name |
| `email` | VARCHAR(255) | NOT NULL | Work email address |
| `phone` | VARCHAR(50) | NOT NULL | Phone / WhatsApp number |
| `job_title` | VARCHAR(100) | NULLABLE | Coordinator title |
| `country` | VARCHAR(100) | NOT NULL | Country of origin |
| `status` | ENUM | NOT NULL, DEFAULT `'PENDING_REVIEW'` | `PENDING_REVIEW`, `APPROVED`, `ALLOCATED`, `REJECTED` |
| `assigned_booth_no` | VARCHAR(50) | NULLABLE | Code assigned upon approval (e.g. `A-04`) |
| `admin_notes` | TEXT | NULLABLE | Internal organizers' review notes |
| `agree_terms` | BOOLEAN | NOT NULL, DEFAULT `true` | Accepted terms agreement |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Submission timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Status update timestamp |

### 2.2 Prisma Model
```prisma
enum BoothAppStatus {
  PENDING_REVIEW
  APPROVED
  ALLOCATED
  REJECTED
}

model BoothApplication {
  id               String         @id @default(uuid())
  referenceNo      String         @unique @map("reference_no")
  eventId          String         @map("event_id")
  event            Event          @relation(fields: [eventId], references: [id], onDelete: Cascade)
  villageId        String         @map("village_id")
  village          ExpoVillage    @relation(fields: [villageId], references: [id], onDelete: Cascade)
  companyName      String         @map("company_name")
  companyWebsite   String?        @map("company_website")
  companySector    String?        @map("company_sector")
  boothPackage     String         @map("booth_package")
  showcaseTitle    String         @map("showcase_title")
  showcaseDesc     String         @map("showcase_desc")
  techRequirements String[]       @default([]) @map("tech_requirements")
  coExhibitors     String?        @map("co_exhibitors")
  firstName        String         @map("first_name")
  lastName         String         @map("last_name")
  email            String
  phone            String
  jobTitle         String?        @map("job_title")
  country          String
  status           BoothAppStatus @default(PENDING_REVIEW)
  assignedBoothNo  String?        @map("assigned_booth_no")
  adminNotes       String?        @map("admin_notes")
  agreeTerms       Boolean        @default(true) @map("agree_terms")
  createdAt        DateTime       @default(now()) @map("created_at")
  updatedAt        DateTime       @updatedAt @map("updated_at")

  @@map("booth_applications")
}
```

---

## 3. API Endpoints

### 3.1 Submit Booth Application
- **Method**: `POST`
- **Path**: `/api/events/:year/register/booth`
- **Auth**: None (Public)

#### Request Payload
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

#### Response `201 Created`
```json
{
  "success": true,
  "referenceNo": "TZ-DPI-BOOTH-849201",
  "message": "Your booth application for GovTech Village has been received.",
  "data": {
    "id": "c71a39f0-2f3b-4890-a3e9-74d128a93e80",
    "referenceNo": "TZ-DPI-BOOTH-849201",
    "village": {
      "slug": "govtech",
      "name": "GovTech Village",
      "hall": "Hall A"
    },
    "companyName": "Selcom Paytech Tanzania Ltd",
    "boothPackage": "Premium Double Booth (6m x 3m)",
    "status": "PENDING_REVIEW",
    "createdAt": "2026-08-28T16:15:00.000Z"
  }
}
```

---

### 3.2 List Booth Applications (Admin)
- **Method**: `GET`
- **Path**: `/api/admin/booths/applications`
- **Auth**: `Bearer <JWT>`

---

### 3.3 Update Application Status & Allocate Booth (Admin)
- **Method**: `PUT`
- **Path**: `/api/admin/booths/applications/:id/status`
- **Auth**: `Bearer <JWT>`

#### Request Payload
```json
{
  "status": "APPROVED",
  "assignedBoothNo": "A-04",
  "adminNotes": "Approved for Government Interoperability Hall A tier."
}
```
