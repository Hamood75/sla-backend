# Street Labs Africa — Backend

Django REST API powering the public website CMS, employee profiles, and the company-wide **Smart QR Platform**.

## Quick start

```bash
cd sla-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_platform
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/`  
Django admin: `http://127.0.0.1:8000/admin/`

### Seeded accounts

| User | Password | Role |
|------|----------|------|
| `admin` | `admin123!` | Super Admin |
| `hamood` | `hamood123!` | Employee |

Demo Smart QR: `/qr/A91KXT` → branded Smart Hub

## Large uploads (hero video)

`PATCH /api/hero/1/` with a background video can return **413 Content Too Large** if the reverse proxy still uses nginx’s default `client_max_body_size 1m`.

Hero clips can be up to **~500 MB**. Django allows **600 MB** (`DATA_UPLOAD_MAX_MEMORY_SIZE`). On the server hosting `api.streetlabsafrica.org`, also set:

```nginx
client_max_body_size 600M;
```

Increase proxy timeouts for slow uploads (e.g. `proxy_read_timeout 600s`). A reference config lives in `nginx.conf`. After changing nginx: `nginx -s reload` (or restart the proxy container).

If Cloudflare (or similar) sits in front of the API, check its upload size limit as well — free plans often cap around 100 MB.

## Architecture

```
/api/cms/homepage/     Public nested homepage payload
/api/profiles/{user}/  Employee digital identity
/api/qr/{code}/        Manage QR codes
/api/qr/resolve/{code}/ Resolve scan → hub or redirect
/api/dashboard/stats/  Backoffice overview
```

Every printed QR points at:

`https://streetlabsafrica.org/qr/{CODE}`

That destination is taken from `PUBLIC_SITE_URL` when the PNG/SVG is generated. Do **not** rely on `FRONTEND_URL` / `DEBUG` for scan URLs — that previously encoded `http://localhost:5173` into production QR images.

After changing `PUBLIC_SITE_URL`, re-download / regenerate QR images in the backoffice so existing codes pick up the new host.

The destination is resolved dynamically (profile, project, event, website, or multi-action Smart Hub).

## Apps

- `accounts` — users, departments, organizations
- `cms` — website content, contact, donations, projects/events/products
- `profiles` — employee public profiles + vCard
- `qr` — Smart QR codes, hub links, image export, analytics
