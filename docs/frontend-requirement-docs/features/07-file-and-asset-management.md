# Feature 07: File & Asset Storage Management API (Admin)

## 1. Overview
The **File & Asset Storage Management API** handles secure, optimized uploads, transformations, and deliveries for all multimedia across event editions:
- **Hero & Background Photography** (Crossfade banners, responsive srcset)
- **Speaker Profile Photos** (Avatars, thumbnail generation)
- **Exhibitor & Sponsor Brand Logos** (SVG, PNG with transparency preservation)
- **Expo Village & Historical Gallery Stream** (High-resolution event photography)
- **Exhibitor Collateral & Documents** (PDF brochures, presentation slides, floor plans)

Supported Storage Drivers:
1. **Cloudinary Engine** (Default for automatic responsive optimization & WebP/AVIF delivery)
2. **AWS S3 / Cloudflare R2 / MinIO** (Object storage for large media & documents)
3. **Local Disk Storage** (Development fallback in `/uploads`)

---

## 2. API Endpoints

### 2.1 Single Media Upload
Uploads a single image or document with automatic compression, dimension validation, and CDN URL generation.

- **Method**: `POST`
- **Path**: `/api/admin/files/upload`
- **Auth**: `Bearer <JWT>`
- **Content-Type**: `multipart/form-data`

#### Form-Data Fields
| Field Name | Type | Description |
|---|---|---|
| `file` | Binary (File) | Image (`jpg`, `jpeg`, `png`, `webp`, `svg`) or Document (`pdf`) |
| `folder` | String | Target storage folder (`heroes`, `speakers`, `villages`, `gallery`, `logos`, `docs`) |
| `altText` | String | Accessibility description / caption |
| `eventId` | UUID (Optional) | Links file metadata to a specific event edition |

#### Response `201 Created`
```json
{
  "success": true,
  "message": "File uploaded and processed successfully",
  "data": {
    "id": "file-89a102bc-3d4e-...",
    "originalName": "govtech_keynote_stage.jpg",
    "mimeType": "image/jpeg",
    "sizeBytes": 1420580,
    "folder": "gallery",
    "url": "https://cdn.tanzaniadpiexpo.org/events/2026/gallery/govtech_keynote_stage.webp",
    "thumbnailUrl": "https://cdn.tanzaniadpiexpo.org/events/2026/gallery/thumbs/govtech_keynote_stage_400x300.webp",
    "dimensions": {
      "width": 1920,
      "height": 1080,
      "aspectRatio": "16:9"
    },
    "altText": "GovTech Village stage keynote presentation",
    "createdAt": "2026-08-28T16:20:00.000Z"
  }
}
```

#### Response `400 Bad Request` (Invalid File Type or Size)
```json
{
  "success": false,
  "error": "File Upload Error",
  "details": "File size exceeds the 10MB limit or unsupported format (.exe)"
}
```

---

### 2.2 Bulk Gallery Upload
Uploads multiple high-resolution photos in a single batch (e.g. 10-50 showcase pictures from previous editions).

- **Method**: `POST`
- **Path**: `/api/admin/files/upload-batch`
- **Auth**: `Bearer <JWT>`
- **Content-Type**: `multipart/form-data`

#### Form-Data Fields
| Field Name | Type | Description |
|---|---|---|
| `files[]` | Binary[] | Array of image files (up to 20 per request) |
| `villageId` | UUID | Associated Expo Village ID |
| `editionYear` | Integer | Historical year (e.g. `2025`, `2024`) |

#### Response `201 Created`
```json
{
  "success": true,
  "uploadedCount": 4,
  "data": [
    {
      "id": "file-01",
      "url": "https://cdn.tanzaniadpiexpo.org/gallery/photo1.webp",
      "title": "Hackathon Winners",
      "caption": "Students presenting smart agritech demo"
    },
    {
      "id": "file-02",
      "url": "https://cdn.tanzaniadpiexpo.org/gallery/photo2.webp",
      "title": "FinTech Workshop",
      "caption": "Panel discussion on instant payments"
    }
  ]
}
```

---

### 2.3 Media Library Browser & Search
Allows administrators to browse existing media files, search by name or folder, and copy asset URLs.

- **Method**: `GET`
- **Path**: `/api/admin/files`
- **Auth**: `Bearer <JWT>`

#### Query Parameters
| Parameter | Type | Default | Description |
|---|---|---|---|
| `folder` | string | `all` | Filter by category (`speakers`, `villages`, `gallery`, `logos`) |
| `search` | string | - | Search by filename or alt text |
| `eventId` | UUID | - | Filter by event edition |
| `page` | integer | `1` | Page number |
| `limit` | integer | `24` | Items per page (grid view) |

#### Response `200 OK`
```json
{
  "success": true,
  "pagination": {
    "total": 148,
    "page": 1,
    "limit": 24,
    "totalPages": 7
  },
  "data": [
    {
      "id": "file-99a",
      "url": "https://cdn.tanzaniadpiexpo.org/speakers/dr_fatma.webp",
      "originalName": "dr_fatma.jpg",
      "folder": "speakers",
      "sizeFormatted": "340 KB",
      "dimensions": "800x800",
      "usedIn": ["Speaker: Dr. Fatma Hassan"],
      "createdAt": "2026-08-20T10:14:00.000Z"
    }
  ]
}
```

---

### 2.4 Delete Asset from Storage
- **Method**: `DELETE`
- **Path**: `/api/admin/files/:id`
- **Auth**: `Bearer <JWT>`

Deletes the asset from Cloudinary/S3/Disk and removes metadata records from PostgreSQL.

#### Response `200 OK`
```json
{
  "success": true,
  "message": "Asset deleted successfully from cloud storage and database"
}
```

---

## 3. Database Schema for File Metadata (`media_assets`)

```prisma
model MediaAsset {
  id           String      @id @default(uuid())
  eventId      String?
  originalName String
  fileName     String
  mimeType     String
  sizeBytes    Int
  folder       String      // "heroes", "speakers", "villages", "gallery", "logos", "docs"
  url          String
  thumbnailUrl String?
  altText      String?
  width        Int?
  height       Int?
  createdAt    DateTime    @default(now())
  updatedAt    DateTime    @updatedAt
}
```

---

## 4. Backend Implementation Blueprint (Express + Multer + Cloudinary)

```ts
import express from 'express'
import multer from 'multer'
import { v2 as cloudinary } from 'cloudinary'
import { CloudinaryStorage } from 'multer-storage-cloudinary'

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
})

const storage = new CloudinaryStorage({
  cloudinary,
  params: async (req, file) => {
    const folder = req.body.folder || 'misc'
    return {
      folder: `tanzania-dpi-expo/${folder}`,
      format: 'webp',
      transformation: [{ quality: 'auto:good' }, { fetch_format: 'auto' }],
    }
  },
})

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
})

const router = express.Router()

router.post('/admin/files/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ success: false, error: 'No file uploaded' })
  }

  // Save metadata to Prisma
  const asset = await prisma.mediaAsset.create({
    data: {
      originalName: req.file.originalname,
      fileName: req.file.filename,
      mimeType: req.file.mimetype,
      sizeBytes: req.file.size,
      folder: req.body.folder || 'misc',
      url: req.file.path,
      altText: req.body.altText,
    }
  })

  return res.status(201).json({ success: true, data: asset })
})

export default router
```
