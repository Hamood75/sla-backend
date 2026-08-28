# Feature 06: Admin Operations & Dashboard Metrics

## 1. Overview
The Admin Operations feature equips event organizers with:
1. **JWT Authentication & Role-Based Access Control** (SuperAdmin, FloorManager, RegistrationDesk)
2. **Dashboard Summary Aggregations** (Total registered attendees by type, booth occupancy % per village, revenue metrics)
3. **Attendee Credential Management & CSV/Excel Export** for badge printing

---

## 2. Database Schema & Tables

### 2.1 Table: `admin_users`
Stores organizer and staff accounts with hashed passwords and role permissions.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique user ID |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | Login email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password string |
| `name` | VARCHAR(150) | NOT NULL | Full name of staff member |
| `role` | ENUM | NOT NULL, DEFAULT `'REGISTRATION_DESK'` | `SUPER_ADMIN`, `FLOOR_MANAGER`, `REGISTRATION_DESK` |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `true` | Account active toggle |
| `last_login_at` | TIMESTAMPTZ | NULLABLE | Last successful login timestamp |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Account creation time |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT `NOW()` | Account update time |

### 2.2 Prisma Model
```prisma
enum AdminRole {
  SUPER_ADMIN
  FLOOR_MANAGER
  REGISTRATION_DESK
}

model AdminUser {
  id           String     @id @default(uuid())
  email        String     @unique
  passwordHash String     @map("password_hash")
  name         String
  role         AdminRole  @default(REGISTRATION_DESK)
  isActive     Boolean    @default(true) @map("is_active")
  lastLoginAt  DateTime?  @map("last_login_at")
  createdAt    DateTime   @default(now()) @map("created_at")
  updatedAt    DateTime   @updatedAt @map("updated_at")

  @@map("admin_users")
}
```

---

## 3. API Endpoints

### 3.1 Admin Login
- **Method**: `POST`
- **Path**: `/api/auth/login`
- **Auth**: None (Public)

#### Request Payload
```json
{
  "email": "admin@tanzaniadpiexpo2026.org",
  "password": "SecurePassword123!"
}
```

#### Response `200 OK`
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "u-01",
    "name": "Expo Admin Lead",
    "email": "admin@tanzaniadpiexpo2026.org",
    "role": "SUPER_ADMIN"
  }
}
```

---

### 3.2 Dashboard Overview Metrics
- **Method**: `GET`
- **Path**: `/api/admin/events/:year/metrics`
- **Auth**: `Bearer <JWT>`

#### Response `200 OK`
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
      { "slug": "govtech", "name": "GovTech Village", "allocatedBooths": 14, "capacity": 16, "occupancyRate": "87.5%" },
      { "slug": "fintech", "name": "FinTech Village", "allocatedBooths": 12, "capacity": 12, "occupancyRate": "100%" },
      { "slug": "youth", "name": "Youth Innovation Hub", "allocatedBooths": 20, "capacity": 25, "occupancyRate": "80%" },
      { "slug": "healthtech", "name": "HealthTech Village", "allocatedBooths": 8, "capacity": 10, "occupancyRate": "80%" },
      { "slug": "agritech", "name": "AgriTech Village", "allocatedBooths": 10, "capacity": 12, "occupancyRate": "83.3%" }
    ],
    "pendingBoothApplications": 7
  }
}
```

---

### 3.3 Export Attendee Badges to CSV
- **Method**: `GET`
- **Path**: `/api/admin/events/:year/export/badges?type=all`
- **Auth**: `Bearer <JWT>`
- **Response**: `text/csv` attachment with headers `[RefNo, Name, Email, Organization, Category, BadgeCode, Status]`
