import hashlib
from io import BytesIO

import qrcode
from django.conf import settings
from qrcode.image.svg import SvgPathImage
from user_agents import parse as parse_ua

from .models import QRCodeAnalytics


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
    """Generate PNG bytes or SVG XML for a QR code pointing at its public URL."""
    url = qr.public_url
    # Prefer frontend local URL in development for testing
    if getattr(settings, 'DEBUG', False) and getattr(settings, 'FRONTEND_URL', None):
        url = f"{settings.FRONTEND_URL.rstrip('/')}{qr.public_path}"

    if fmt == 'svg':
        img = qrcode.make(url, image_factory=SvgPathImage)
        buffer = BytesIO()
        img.save(buffer)
        return buffer.getvalue(), 'image/svg+xml'

    qr_obj = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr_obj.add_data(url)
    qr_obj.make(fit=True)
    img = qr_obj.make_image(fill_color=qr.secondary_color or '#0a1f44', back_color=qr.background_color or 'white')

    if qr.show_logo and qr.logo:
        try:
            from PIL import Image
            logo = Image.open(qr.logo.path).convert('RGBA')
            qr_w, qr_h = img.size
            logo_size = qr_w // 4
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
            img = img.convert('RGBA')
            img.paste(logo, pos, logo)
        except Exception:
            pass

    buffer = BytesIO()
    img.convert('RGB').save(buffer, format='PNG')
    return buffer.getvalue(), 'image/png'
