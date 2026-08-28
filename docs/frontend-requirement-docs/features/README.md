# SLA Events API — Feature Specifications

This directory contains detailed technical requirements, API routes, request payloads, response structures, and validation rules for each core subsystem of the **SLA Events Backend**.

## Feature Directory

| Index | Feature Specification | Description |
|---|---|---|
| 01 | [Events Management](file:///Users/mac/development/vueprojects/sla-events/docs/features/01-events-management.md) | Multi-year event editions, hero slideshow crossfade, active edition resolution, and venue GPS metadata. |
| 02 | [Expo Villages](file:///Users/mac/development/vueprojects/sla-events/docs/features/02-expo-villages.md) | Thematic exhibition zones (`GovTech`, `FinTech`, `Youth Hub`, `HealthTech`, `AgriTech`), slug-based lookups, hall assignments, and quick metrics. |
| 03 | [Booth & Exhibitor Registration](file:///Users/mac/development/vueprojects/sla-events/docs/features/03-booth-and-exhibitor-registration.md) | Dedicated village booth applications, stand packages, live demo specs, technical requirements, and allocation approval workflow. |
| 04 | [General Registrations](file:///Users/mac/development/vueprojects/sla-events/docs/features/04-general-registrations.md) | Guest/Delegate badges, Call for Speakers proposals, and Volunteer operations crew applications. |
| 05 | [Speakers & Program Schedule](file:///Users/mac/development/vueprojects/sla-events/docs/features/05-speakers-and-program-schedule.md) | Keynotes, panel discussions, and multi-day stage timetable. |
| 06 | [Admin Operations & Metrics](file:///Users/mac/development/vueprojects/sla-events/docs/features/06-admin-and-operations.md) | JWT authentication, dashboard aggregations, booth occupancy rates, and attendee CSV badge exports. |
| 07 | [File & Asset Management API](file:///Users/mac/development/vueprojects/sla-events/docs/features/07-file-and-asset-management.md) | Multi-part media uploads (Cloudinary/S3/Disk), automatic WebP optimization, media library browser, and asset deletion. |

---

## Global System Conventions

1. **Base URL**: `https://api.tanzaniadpiexpo.org` (Local: `http://localhost:3000`)
2. **Standard Success Envelope**:
   ```json
   {
     "success": true,
     "message": "Optional human-readable confirmation",
     "data": {}
   }
   ```
3. **Standard Error Envelope**:
   ```json
   {
     "success": false,
     "error": "Error title or description",
     "details": {}
   }
   ```
4. **Time & Date standard**: ISO-8601 UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`).
