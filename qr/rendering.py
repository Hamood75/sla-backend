"""Branded Street Labs QR rendering — rounded modules, tricolor bands, logo badge."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw

BRAND_NAVY = '#0a1f44'
BRAND_ORANGE = '#ff6a00'
BRAND_GREEN = '#0a7a3d'
DEFAULT_LOGO = Path(__file__).resolve().parent / 'assets' / 'default_logo.png'

# Center badge — full wordmark inside a large smooth white circle (see brand QR reference).
BADGE_BODY_RATIO = 0.34
LOGO_FILL_RATIO = 0.88
BADGE_SUPERSAMPLE = 2

FINDER_PATTERN = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
]


def _hex(color: str | None, fallback: str) -> str:
    value = (color or '').strip()
    if value.startswith('#') and len(value) in (4, 7):
        return value
    if len(value) in (3, 6) and all(c in '0123456789abcdefABCDEF' for c in value):
        return f'#{value}'
    return fallback


def _band_color(row: int, size: int, navy: str, orange: str, green: str) -> str:
    if size <= 1:
        return navy
    t = row / (size - 1)
    if t < 1 / 3:
        return navy
    if t < 2 / 3:
        return orange
    return green


def _in_finder(row: int, col: int, size: int) -> bool:
    if row < 7 and col < 7:
        return True
    if row < 7 and col >= size - 7:
        return True
    if row >= size - 7 and col < 7:
        return True
    return False


def _finder_eye_color(finder: str, navy: str, orange: str, green: str) -> str:
    if finder == 'tr':
        return orange
    if finder == 'bl':
        return green
    return navy


def _finder_origin(finder: str, size: int) -> tuple[int, int]:
    if finder == 'tr':
        return (0, size - 7)
    if finder == 'bl':
        return (size - 7, 0)
    return (0, 0)


def _build_matrix(url: str):
    qr_obj = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=0,
    )
    qr_obj.add_data(url)
    qr_obj.make(fit=True)
    return qr_obj.modules


def _load_logo(qr) -> Image.Image | None:
    if not getattr(qr, 'show_logo', True):
        return None
    path = None
    if getattr(qr, 'logo', None):
        try:
            path = qr.logo.path
        except Exception:
            path = None
    if not path and DEFAULT_LOGO.exists():
        path = str(DEFAULT_LOGO)
    if not path:
        return None
    try:
        return Image.open(path).convert('RGBA')
    except Exception:
        return None


def _draw_circle(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, fill: str):
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill)


def _draw_finder(
    draw: ImageDraw.ImageDraw,
    finder: str,
    size: int,
    module: float,
    origin_x: float,
    origin_y: float,
    radius: float,
    color_for_row,
    navy: str,
    orange: str,
    green: str,
):
    origin_row, origin_col = _finder_origin(finder, size)
    for r in range(7):
        for c in range(7):
            if 2 <= r <= 4 and 2 <= c <= 4:
                continue
            if not FINDER_PATTERN[r][c]:
                continue
            row = origin_row + r
            col = origin_col + c
            cx = origin_x + (col + 0.5) * module
            cy = origin_y + (row + 0.5) * module
            _draw_circle(draw, cx, cy, radius, color_for_row(row))

    x0 = origin_x + (origin_col + 2) * module
    y0 = origin_y + (origin_row + 2) * module
    x1 = origin_x + (origin_col + 5) * module
    y1 = origin_y + (origin_row + 5) * module
    pad = module * 0.08
    draw.rounded_rectangle(
        (x0 + pad, y0 + pad, x1 - pad, y1 - pad),
        radius=module * 0.45,
        fill=_finder_eye_color(finder, navy, orange, green),
    )


def _draw_frame(
    draw: ImageDraw.ImageDraw,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    stroke: int,
    navy: str,
    orange: str,
    green: str,
):
    radius = 18
    mid_x = (x0 + x1) / 2

    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, outline=navy, width=stroke)

    # Top-left + left stay navy
    draw.arc((x0, y0, x0 + 2 * radius, y0 + 2 * radius), 180, 270, fill=navy, width=stroke)
    draw.line((x0 + radius, y0, mid_x, y0), fill=navy, width=stroke)
    draw.line((x0, y0 + radius, x0, y1 - radius), fill=navy, width=stroke)

    # Top-right + right in orange
    draw.line((mid_x, y0, x1 - radius, y0), fill=orange, width=stroke)
    draw.arc((x1 - 2 * radius, y0, x1, y0 + 2 * radius), 270, 360, fill=orange, width=stroke)
    draw.line((x1, y0 + radius, x1, y1 - radius), fill=orange, width=stroke)

    # Bottom in green
    draw.arc((x0, y1 - 2 * radius, x0 + 2 * radius, y1), 90, 180, fill=green, width=stroke)
    draw.arc((x1 - 2 * radius, y1 - 2 * radius, x1, y1), 0, 90, fill=green, width=stroke)
    draw.line((x0 + radius, y1, x1 - radius, y1), fill=green, width=stroke)


def _badge_diameter(body: float) -> int:
    return int(body * BADGE_BODY_RATIO)


def _build_logo_badge(logo: Image.Image, badge_d: int) -> Image.Image:
    scale = BADGE_SUPERSAMPLE
    d = max(1, badge_d * scale)
    badge = Image.new('RGBA', (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(badge).ellipse((0, 0, d - 1, d - 1), fill=(255, 255, 255, 255))

    inner = int(d * LOGO_FILL_RATIO)
    fit = logo.copy()
    fit.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    badge.paste(fit, ((d - fit.width) // 2, (d - fit.height) // 2), fit)

    if scale > 1:
        badge = badge.resize((badge_d, badge_d), Image.Resampling.LANCZOS)
    return badge


def _paste_logo_badge(
    canvas: Image.Image,
    logo: Image.Image,
    center_x: float,
    center_y: float,
    badge_d: int,
):
    badge = _build_logo_badge(logo, badge_d)
    r = badge_d / 2
    canvas.alpha_composite(badge, dest=(int(center_x - r), int(center_y - r)))


def render_branded_qr_png(url: str, qr) -> bytes:
    matrix = _build_matrix(url)
    size = len(matrix)
    navy = _hex(getattr(qr, 'secondary_color', None), BRAND_NAVY)
    orange = _hex(getattr(qr, 'primary_color', None), BRAND_ORANGE)
    green = BRAND_GREEN
    bg = _hex(getattr(qr, 'background_color', None), '#ffffff')

    render_scale = 3
    module = 14 * render_scale
    quiet = module * 3
    frame_pad = int(module * 1.2)
    body = size * module
    canvas_size = int(quiet * 2 + body + frame_pad * 2)
    ox = oy = float(frame_pad)
    origin_x = ox + quiet
    origin_y = oy + quiet
    radius = module * 0.42

    canvas = Image.new('RGBA', (canvas_size, canvas_size), bg)
    draw = ImageDraw.Draw(canvas)

    def color_for_row(row: int) -> str:
        return _band_color(row, size, navy, orange, green)

    for r in range(size):
        for c in range(size):
            if not matrix[r][c] or _in_finder(r, c, size):
                continue
            cx = origin_x + (c + 0.5) * module
            cy = origin_y + (r + 0.5) * module
            _draw_circle(draw, cx, cy, radius, color_for_row(r))

    for finder in ('tl', 'tr', 'bl'):
        _draw_finder(
            draw,
            finder,
            size,
            module,
            origin_x,
            origin_y,
            radius,
            color_for_row,
            navy,
            orange,
            green,
        )

    inset = frame_pad * 0.35
    _draw_frame(
        draw,
        inset,
        inset,
        canvas_size - inset,
        canvas_size - inset,
        max(3, module // 4),
        navy,
        orange,
        green,
    )

    logo = _load_logo(qr)
    if logo is not None:
        badge_d = _badge_diameter(body)
        _paste_logo_badge(
            canvas,
            logo,
            origin_x + body / 2,
            origin_y + body / 2,
            badge_d,
        )

    output_size = canvas_size // render_scale
    canvas = canvas.resize((output_size, output_size), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    canvas.convert('RGB').save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()


def render_branded_qr_svg(url: str, qr) -> bytes:
    matrix = _build_matrix(url)
    size = len(matrix)
    navy = _hex(getattr(qr, 'secondary_color', None), BRAND_NAVY)
    orange = _hex(getattr(qr, 'primary_color', None), BRAND_ORANGE)
    green = BRAND_GREEN
    bg = _hex(getattr(qr, 'background_color', None), '#ffffff')

    module = 10.0
    quiet = module * 3
    frame_pad = module * 1.2
    body = size * module
    canvas = quiet * 2 + body + frame_pad * 2
    origin_x = frame_pad + quiet
    origin_y = frame_pad + quiet
    radius = module * 0.42

    def color_for_row(row: int) -> str:
        return _band_color(row, size, navy, orange, green)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas:.0f}" height="{canvas:.0f}" '
        f'viewBox="0 0 {canvas:.2f} {canvas:.2f}" shape-rendering="geometricPrecision">',
        f'<rect width="100%" height="100%" fill="{bg}"/>',
    ]

    for r in range(size):
        for c in range(size):
            if not matrix[r][c] or _in_finder(r, c, size):
                continue
            cx = origin_x + (c + 0.5) * module
            cy = origin_y + (r + 0.5) * module
            parts.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" fill="{color_for_row(r)}"/>'
            )

    for finder in ('tl', 'tr', 'bl'):
        origin_row, origin_col = _finder_origin(finder, size)
        for r in range(7):
            for c in range(7):
                if 2 <= r <= 4 and 2 <= c <= 4:
                    continue
                if not FINDER_PATTERN[r][c]:
                    continue
                row = origin_row + r
                col = origin_col + c
                cx = origin_x + (col + 0.5) * module
                cy = origin_y + (row + 0.5) * module
                parts.append(
                    f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" fill="{color_for_row(row)}"/>'
                )
        x0 = origin_x + (origin_col + 2) * module
        y0 = origin_y + (origin_row + 2) * module
        pad = module * 0.08
        rw = 3 * module - 2 * pad
        eye = _finder_eye_color(finder, navy, orange, green)
        parts.append(
            f'<rect x="{x0 + pad:.2f}" y="{y0 + pad:.2f}" width="{rw:.2f}" height="{rw:.2f}" '
            f'rx="{module * 0.45:.2f}" fill="{eye}"/>'
        )

    inset = frame_pad * 0.35
    stroke = max(2, int(module // 4))
    parts.append(
        f'<rect x="{inset:.2f}" y="{inset:.2f}" width="{canvas - 2 * inset:.2f}" '
        f'height="{canvas - 2 * inset:.2f}" rx="14" fill="none" stroke="{navy}" '
        f'stroke-width="{stroke}"/>'
    )

    logo = _load_logo(qr)
    if logo is not None:
        badge_d = _badge_diameter(body)
        cx = origin_x + body / 2
        cy = origin_y + body / 2
        badge = _build_logo_badge(logo, badge_d)
        buf = BytesIO()
        badge.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        parts.append(
            f'<image href="data:image/png;base64,{b64}" x="{cx - badge_d / 2:.2f}" '
            f'y="{cy - badge_d / 2:.2f}" width="{badge_d}" height="{badge_d}"/>'
        )

    parts.append('</svg>')
    return '\n'.join(parts).encode('utf-8')
