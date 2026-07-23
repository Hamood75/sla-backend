"""Shared outbound email helpers for Street Labs Africa."""

from __future__ import annotations

import logging
from email.mime.image import MIMEImage
from html import escape
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from .models import ContactMessage, MeetingRequest, SiteSettings

logger = logging.getLogger(__name__)

LOGO_CID = 'sla-logo'
LOGO_PATH = Path(__file__).resolve().parent / 'email_assets' / 'logo.png'


def org_identity():
    org = SiteSettings.load()
    org_name = (org.org_name or 'Street Digital Labs Africa').strip()
    org_inbox = (org.email or '').strip() or 'info@streetlabsafrica.org'
    noreply = (getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@streetlabsafrica.org').strip()
    from_email = f'{org_name} <{noreply}>'
    return org, org_name, org_inbox, noreply, from_email


def notify_inboxes() -> list[str]:
    """Org inboxes that should receive contact/meeting alerts."""
    _, _, org_inbox, _, _ = org_identity()
    extra = (getattr(settings, 'CONTACT_NOTIFY_EMAIL', None) or '').strip()
    addresses = [org_inbox]
    if extra:
        addresses.extend(part.strip() for part in extra.split(',') if part.strip())
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for addr in addresses:
        key = addr.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(addr)
    return unique


def _paragraphs_html(text: str) -> str:
    parts = [escape(p.strip()) for p in (text or '').split('\n') if p.strip()]
    if not parts:
        return ''
    return ''.join(f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">{p}</p>' for p in parts)


def _kv_rows(rows: list[tuple[str, str]]) -> str:
    cells = []
    for label, value in rows:
        if not value:
            continue
        cells.append(
            '<tr>'
            f'<td style="padding:6px 12px 6px 0;color:#64748b;font-size:13px;vertical-align:top;white-space:nowrap;">{escape(label)}</td>'
            f'<td style="padding:6px 0;color:#0a1f44;font-size:14px;font-weight:600;">{escape(value)}</td>'
            '</tr>'
        )
    if not cells:
        return ''
    return f'<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;margin:16px 0;">{"".join(cells)}</table>'


def render_branded_email(*, title: str, intro_html: str, details_html: str = '', footer_note: str = '') -> tuple[str, str]:
    """Return (plain_text, html) for a branded SLA email."""
    _, org_name, _, _, _ = org_identity()
    site = (getattr(settings, 'PUBLIC_SITE_URL', None) or 'https://streetlabsafrica.org').rstrip('/')
    note = footer_note or (
        'This is an automated message from noreply@streetlabsafrica.org. Please do not reply to this address.'
    )

    plain_intro = (
        intro_html.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    )
    plain = (
        f'{title}\n\n'
        f'{plain_intro}\n\n'
        f'{org_name}\n{site}\n\n{note}'
    )
    html = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:Poppins,Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:28px 12px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e6ebf2;">
        <tr>
          <td style="background:#0a1f44;padding:22px 28px;text-align:center;">
            <img src="cid:{LOGO_CID}" alt="{escape(org_name)}" width="180" style="display:inline-block;max-width:180px;height:auto;border:0;" />
          </td>
        </tr>
        <tr>
          <td style="height:4px;background:linear-gradient(90deg,#0a7a3d 0%,#ffffff 50%,#ff6a00 100%);font-size:0;line-height:0;">&nbsp;</td>
        </tr>
        <tr>
          <td style="padding:28px 28px 8px;">
            <h1 style="margin:0 0 16px;font-size:20px;line-height:1.3;color:#0a1f44;font-weight:700;">{escape(title)}</h1>
            {intro_html}
            {details_html}
          </td>
        </tr>
        <tr>
          <td style="padding:8px 28px 28px;">
            <p style="margin:20px 0 0;padding-top:16px;border-top:1px solid #e6ebf2;color:#0a1f44;font-size:14px;font-weight:700;">{escape(org_name)}</p>
            <p style="margin:4px 0 0;"><a href="{escape(site)}" style="color:#ff6a00;font-size:13px;text-decoration:none;">{escape(site.replace("https://", "").replace("http://", ""))}</a></p>
            <p style="margin:14px 0 0;color:#94a3b8;font-size:12px;line-height:1.5;">{escape(note)}</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>'''
    return plain, html


def send_mail_safe(
    *,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    to: list[str],
    reply_to: list[str] | None = None,
) -> bool:
    _, _, _, _, from_email = org_identity()
    recipients = [addr for addr in to if addr]
    if not recipients:
        return False
    try:
        mail = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=recipients,
            reply_to=reply_to or None,
        )
        if html_body:
            mail.attach_alternative(html_body, 'text/html')
            if LOGO_PATH.is_file():
                with LOGO_PATH.open('rb') as fh:
                    logo = MIMEImage(fh.read(), _subtype='png')
                logo.add_header('Content-ID', f'<{LOGO_CID}>')
                logo.add_header('Content-Disposition', 'inline', filename='logo.png')
                mail.mixed_subtype = 'related'
                mail.attach(logo)
        mail.send(fail_silently=False)
        return True
    except Exception:
        logger.exception('Failed to send email to %s — subject=%r', recipients, subject)
        return False


def send_mail_each(
    *,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    to: list[str],
    reply_to: list[str] | None = None,
) -> int:
    """Send the same message to each recipient separately. Returns success count."""
    return sum(
        1
        for addr in to
        if send_mail_safe(
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            to=[addr],
            reply_to=reply_to,
        )
    )


def notify_contact_received(msg: ContactMessage) -> None:
    """Email confirmation to the sender + alert the org inbox(es)."""
    _, org_name, org_inbox, _, _ = org_identity()
    subject_line = (msg.subject or '').strip() or 'General enquiry'

    # Sender confirmation first — never blocked by a bad org mailbox.
    confirm_text = (
        f'Hi {msg.name},\n\n'
        f'Thank you for contacting {org_name}. We have received your message and will get back to you shortly.\n\n'
        f'Subject: {subject_line}\n\n'
        f'Your message:\n{msg.message.strip()}\n\n'
        f'—\n{org_name}\n'
        f'This is an automated confirmation from noreply@streetlabsafrica.org.\n'
        f'Please do not reply to this address.'
    )
    confirm_intro = (
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">Hi {escape(msg.name)},</p>'
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">'
        f'Thank you for contacting <strong>{escape(org_name)}</strong>. '
        f'We have received your message and will get back to you shortly.</p>'
    )
    confirm_details = _kv_rows([('Subject', subject_line)]) + (
        f'<p style="margin:16px 0 8px;color:#64748b;font-size:12px;font-weight:700;letter-spacing:0.06em;'
        f'text-transform:uppercase;">Your message</p>'
        f'<div style="padding:14px 16px;background:#f8fafc;border-radius:8px;border:1px solid #e6ebf2;'
        f'color:#334155;font-size:14px;line-height:1.6;">'
        f'{escape(msg.message.strip()).replace(chr(10), "<br>")}</div>'
    )
    _, confirm_html = render_branded_email(
        title='We received your message',
        intro_html=confirm_intro,
        details_html=confirm_details,
    )
    send_mail_safe(
        subject=f'We received your message — {org_name}',
        text_body=confirm_text,
        html_body=confirm_html,
        to=[msg.email],
        reply_to=[org_inbox],
    )

    internal_text = (
        f'New contact form message\n\n'
        f'From: {msg.name} <{msg.email}>\n'
        f'Subject: {subject_line}\n\n'
        f'{msg.message.strip()}\n\n'
        f'—\n{org_name} backoffice → Messages'
    )
    internal_html_intro = (
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">'
        f'New message from <strong>{escape(msg.name)}</strong> '
        f'(<a href="mailto:{escape(msg.email)}" style="color:#ff6a00;">{escape(msg.email)}</a>).'
        f'</p>'
    )
    internal_details = _kv_rows([('Subject', subject_line)]) + (
        f'<div style="margin-top:8px;padding:14px 16px;background:#f8fafc;border-radius:8px;'
        f'border:1px solid #e6ebf2;color:#334155;font-size:14px;line-height:1.6;">'
        f'{escape(msg.message.strip()).replace(chr(10), "<br>")}</div>'
    )
    _, internal_html = render_branded_email(
        title='New contact message',
        intro_html=internal_html_intro,
        details_html=internal_details,
        footer_note=f'{org_name} backoffice → Messages',
    )
    send_mail_each(
        subject=f'Contact: {subject_line}',
        text_body=internal_text,
        html_body=internal_html,
        to=notify_inboxes(),
        reply_to=[msg.email],
    )


def notify_meeting_request(meeting: MeetingRequest) -> None:
    """Email the official/org + confirmation to the requester."""
    _, org_name, org_inbox, _, _ = org_identity()
    official = meeting.official
    preferred = timezone.localtime(meeting.preferred_at).strftime('%d %b %Y, %I:%M %p')
    topic = meeting.topic.strip() or 'General meeting'

    recipients = []
    if (official.email or '').strip():
        recipients.append(official.email.strip())
    for addr in notify_inboxes():
        if addr not in recipients:
            recipients.append(addr)

    official_text_lines = [
        f'Hi {official.name},',
        '',
        'You have a new meeting request via Street Labs Africa.',
        '',
        f'Requester: {meeting.name}',
        f'Email: {meeting.email}',
    ]
    if meeting.phone:
        official_text_lines.append(f'Phone: {meeting.phone}')
    if meeting.organization:
        official_text_lines.append(f'Organization: {meeting.organization}')
    official_text_lines.extend([f'Preferred time: {preferred}', f'Topic: {topic}'])
    if meeting.message.strip():
        official_text_lines.extend(['', 'Message:', meeting.message.strip()])
    official_text_lines.extend(['', '—', org_name, 'Review this request in the backoffice → Meetings.'])

    official_intro = (
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">Hi {escape(official.name)},</p>'
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">'
        f'You have a new meeting request via Street Labs Africa.</p>'
    )
    official_details = _kv_rows([
        ('Requester', meeting.name),
        ('Email', meeting.email),
        ('Phone', meeting.phone or ''),
        ('Organization', meeting.organization or ''),
        ('Preferred time', preferred),
        ('Topic', topic),
    ])
    if meeting.message.strip():
        official_details += (
            f'<p style="margin:16px 0 8px;color:#64748b;font-size:12px;font-weight:700;letter-spacing:0.06em;'
            f'text-transform:uppercase;">Message</p>'
            f'<div style="padding:14px 16px;background:#f8fafc;border-radius:8px;border:1px solid #e6ebf2;'
            f'color:#334155;font-size:14px;line-height:1.6;">'
            f'{escape(meeting.message.strip()).replace(chr(10), "<br>")}</div>'
        )
    _, official_html = render_branded_email(
        title='New meeting request',
        intro_html=official_intro,
        details_html=official_details,
        footer_note='Review this request in the backoffice → Meetings.',
    )
    send_mail_each(
        subject=f'New meeting request from {meeting.name}',
        text_body='\n'.join(official_text_lines),
        html_body=official_html,
        to=recipients,
        reply_to=[meeting.email],
    )

    confirm_text = (
        f'Hi {meeting.name},\n\n'
        f'Thank you for booking a meeting with {official.name} at {org_name}.\n'
        f'We have received your request and will confirm shortly by email.\n\n'
        f'With: {official.name} ({official.role})\n'
        f'Preferred time: {preferred}\n'
        f'Topic: {topic}\n'
    )
    if meeting.message.strip():
        confirm_text += f'\nYour notes:\n{meeting.message.strip()}\n'
    confirm_text += (
        f'\n—\n{org_name}\n'
        f'This is an automated confirmation from noreply@streetlabsafrica.org.\n'
        f'Please do not reply to this address.'
    )
    confirm_intro = (
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">Hi {escape(meeting.name)},</p>'
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">'
        f'Thank you for booking a meeting with <strong>{escape(official.name)}</strong> at '
        f'<strong>{escape(org_name)}</strong>. We have received your request and will confirm shortly by email.</p>'
    )
    confirm_details = _kv_rows([
        ('With', f'{official.name} ({official.role})'),
        ('Preferred time', preferred),
        ('Topic', topic),
    ])
    if meeting.message.strip():
        confirm_details += (
            f'<p style="margin:16px 0 8px;color:#64748b;font-size:12px;font-weight:700;letter-spacing:0.06em;'
            f'text-transform:uppercase;">Your notes</p>'
            f'<div style="padding:14px 16px;background:#f8fafc;border-radius:8px;border:1px solid #e6ebf2;'
            f'color:#334155;font-size:14px;line-height:1.6;">'
            f'{escape(meeting.message.strip()).replace(chr(10), "<br>")}</div>'
        )
    _, confirm_html = render_branded_email(
        title='Meeting request received',
        intro_html=confirm_intro,
        details_html=confirm_details,
    )
    send_mail_safe(
        subject=f'Meeting request received — {org_name}',
        text_body=confirm_text,
        html_body=confirm_html,
        to=[meeting.email],
        reply_to=[org_inbox],
    )


def send_contact_reply(*, msg: ContactMessage, body: str, subject: str) -> bool:
    """Branded HTML reply from backoffice to a contact sender."""
    _, org_name, org_inbox, _, _ = org_identity()
    text_body = (
        f'Hi {msg.name},\n\n'
        f'{body}\n\n'
        f'—\n{org_name}\n{org_inbox}\n\n'
        f'---\nOn your message:\n{msg.message}\n'
    )
    intro = (
        f'<p style="margin:0 0 12px;color:#334155;font-size:15px;line-height:1.6;">Hi {escape(msg.name)},</p>'
        f'{_paragraphs_html(body)}'
    )
    details = (
        f'<p style="margin:20px 0 8px;color:#64748b;font-size:12px;font-weight:700;letter-spacing:0.06em;'
        f'text-transform:uppercase;">Your original message</p>'
        f'<div style="padding:14px 16px;background:#f8fafc;border-radius:8px;border:1px solid #e6ebf2;'
        f'color:#64748b;font-size:13px;line-height:1.6;">'
        f'{escape(msg.message).replace(chr(10), "<br>")}</div>'
    )
    _, html_body = render_branded_email(
        title=subject,
        intro_html=intro,
        details_html=details,
        footer_note=f'Reply to this email goes to {org_inbox}.',
    )
    return send_mail_safe(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        to=[msg.email],
        reply_to=[org_inbox],
    )
