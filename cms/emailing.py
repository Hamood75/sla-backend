"""Shared outbound email helpers for Street Labs Africa."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import ContactMessage, MeetingRequest, SiteSettings

logger = logging.getLogger(__name__)


def org_identity():
    org = SiteSettings.load()
    org_name = (org.org_name or 'Street Digital Labs Africa').strip()
    org_inbox = (org.email or '').strip() or 'info@streetlabsafrica.org'
    noreply = (getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@streetlabsafrica.org').strip()
    from_email = f'{org_name} <{noreply}>'
    return org, org_name, org_inbox, noreply, from_email


def send_mail_safe(*, subject: str, body: str, to: list[str], reply_to: list[str] | None = None) -> bool:
    _, _, _, _, from_email = org_identity()
    recipients = [addr for addr in to if addr]
    if not recipients:
        return False
    try:
        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=recipients,
            reply_to=reply_to or None,
        )
        mail.send(fail_silently=False)
        return True
    except Exception:
        logger.exception('Failed to send email to %s — subject=%r', recipients, subject)
        return False


def notify_contact_received(msg: ContactMessage) -> None:
    """Email the org inbox + confirmation to the sender."""
    _, org_name, org_inbox, _, _ = org_identity()
    subject_line = (msg.subject or '').strip() or 'General enquiry'

    # Internal notification
    internal_lines = [
        'New contact form message',
        '',
        f'From: {msg.name} <{msg.email}>',
        f'Subject: {subject_line}',
        '',
        msg.message.strip(),
        '',
        '—',
        f'{org_name} backoffice → Messages',
    ]
    send_mail_safe(
        subject=f'Contact: {subject_line}',
        body='\n'.join(internal_lines),
        to=[org_inbox],
        reply_to=[msg.email],
    )

    # Sender confirmation
    confirm_lines = [
        f'Hi {msg.name},',
        '',
        f'Thank you for contacting {org_name}. We have received your message and will get back to you shortly.',
        '',
        f'Subject: {subject_line}',
        '',
        'Your message:',
        msg.message.strip(),
        '',
        '—',
        org_name,
        'This is an automated confirmation from noreply@streetlabsafrica.org.',
        'Please do not reply to this address.',
    ]
    send_mail_safe(
        subject=f'We received your message — {org_name}',
        body='\n'.join(confirm_lines),
        to=[msg.email],
        reply_to=[org_inbox],
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
    if org_inbox and org_inbox not in recipients:
        recipients.append(org_inbox)

    official_lines = [
        f'Hi {official.name},',
        '',
        'You have a new meeting request via Street Labs Africa.',
        '',
        f'Requester: {meeting.name}',
        f'Email: {meeting.email}',
    ]
    if meeting.phone:
        official_lines.append(f'Phone: {meeting.phone}')
    if meeting.organization:
        official_lines.append(f'Organization: {meeting.organization}')
    official_lines.extend([
        f'Preferred time: {preferred}',
        f'Topic: {topic}',
    ])
    if meeting.message.strip():
        official_lines.extend(['', 'Message:', meeting.message.strip()])
    official_lines.extend([
        '',
        '—',
        org_name,
        'Review this request in the backoffice → Meetings.',
    ])
    send_mail_safe(
        subject=f'New meeting request from {meeting.name}',
        body='\n'.join(official_lines),
        to=recipients,
        reply_to=[meeting.email],
    )

    confirm_lines = [
        f'Hi {meeting.name},',
        '',
        f'Thank you for booking a meeting with {official.name} at {org_name}.',
        'We have received your request and will confirm shortly by email.',
        '',
        f'With: {official.name} ({official.role})',
        f'Preferred time: {preferred}',
        f'Topic: {topic}',
    ]
    if meeting.message.strip():
        confirm_lines.extend(['', 'Your notes:', meeting.message.strip()])
    confirm_lines.extend([
        '',
        '—',
        org_name,
        'This is an automated confirmation from noreply@streetlabsafrica.org.',
        'Please do not reply to this address.',
    ])
    send_mail_safe(
        subject=f'Meeting request received — {org_name}',
        body='\n'.join(confirm_lines),
        to=[meeting.email],
        reply_to=[org_inbox],
    )
