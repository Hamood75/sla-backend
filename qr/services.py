import hashlib

from django.conf import settings
from user_agents import parse as parse_ua

from .models import QRCodeAnalytics
from .rendering import render_branded_qr_png, render_branded_qr_svg


def hash_ip(ip: str) -> str:
    if not ip:
        return ''
    salt = getattr(settings, 'SECRET_KEY', 'sla')[:16]
    return hashlib.sha256(f'{salt}:{ip}'.encode()).hexdigest()


def record_scan(qr, request, link_clicked=None):
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    ua = parse_ua(ua_string)
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    ip_digest = hash_ip(ip)

    is_returning = False
    if ip_digest:
        is_returning = QRCodeAnalytics.objects.filter(qr=qr, ip_hash=ip_digest).exists()

    device = 'mobile' if ua.is_mobile else 'tablet' if ua.is_tablet else 'pc' if ua.is_pc else 'other'
    browser = ua.browser.family or ''
    os_name = ua.os.family or ''

    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    try:
        latitude = float(lat) if lat not in (None, '') else None
        longitude = float(lng) if lng not in (None, '') else None
    except (TypeError, ValueError):
        latitude = longitude = None

    country = ''
    if hasattr(request, 'data') and isinstance(getattr(request, 'data', None), dict):
        country = request.data.get('country', '') or ''

    QRCodeAnalytics.objects.create(
        qr=qr,
        country=country,
        city=request.query_params.get('city', ''),
        device=device,
        browser=browser,
        os=os_name,
        referrer=request.META.get('HTTP_REFERER', '')[:500],
        ip_hash=ip_digest,
        user_agent=ua_string[:1000],
        is_returning=is_returning,
        link_clicked=link_clicked,
        latitude=latitude,
        longitude=longitude,
    )
    qr.scan_count += 1
    qr.save(update_fields=['scan_count'])


def build_qr_image(qr, fmt='png'):
    """Generate branded PNG/SVG for a QR code pointing at its public URL."""
    url = qr.public_url
    if getattr(settings, 'DEBUG', False) and getattr(settings, 'FRONTEND_URL', None):
        url = f"{settings.FRONTEND_URL.rstrip('/')}{qr.public_path}"

    if fmt == 'svg':
        return render_branded_qr_svg(url, qr), 'image/svg+xml'
    return render_branded_qr_png(url, qr), 'image/png'
