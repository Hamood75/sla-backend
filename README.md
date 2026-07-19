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

The destination is resolved dynamically (profile, project, event, website, or multi-action Smart Hub).

## Apps

- `accounts` — users, departments, organizations
- `cms` — website content, contact, donations, projects/events/products
- `profiles` — employee public profiles + vCard
- `qr` — Smart QR codes, hub links, image export, analytics
