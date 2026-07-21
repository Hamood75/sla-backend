import secrets
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


def generate_qr_code():
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(alphabet) for _ in range(6))


class QRCode(models.Model):
    class DestinationType(models.TextChoices):
        HUB = 'hub', 'Smart Hub'
        PROFILE = 'profile', 'Employee Profile'
        PROJECT = 'project', 'Project'
        EVENT = 'event', 'Event'
        PRODUCT = 'product', 'Product'
        ORGANIZATION = 'organization', 'Organization'
        WEBSITE = 'website', 'Website'
        SOCIAL = 'social', 'Social'
        CUSTOM = 'custom', 'Custom URL'

    class Theme(models.TextChoices):
        BRAND = 'brand', 'Street Labs Brand'
        DARK = 'dark', 'Dark'
        LIGHT = 'light', 'Light'
        CUSTOM = 'custom', 'Custom'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, unique=True, default=generate_qr_code, db_index=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qr_codes',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    destination_type = models.CharField(
        max_length=32,
        choices=DestinationType.choices,
        default=DestinationType.HUB,
    )
    # Dynamic destination via generic relation or direct URL
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    destination_object = GenericForeignKey('content_type', 'object_id')
    destination_url = models.URLField(blank=True)

    theme = models.CharField(max_length=20, choices=Theme.choices, default=Theme.BRAND)
    primary_color = models.CharField(max_length=20, default='#ff6a00')
    secondary_color = models.CharField(max_length=20, default='#0a1f44')
    background_color = models.CharField(max_length=20, default='#ffffff')
    logo = models.ImageField(upload_to='qr/logos/', blank=True, null=True)
    show_logo = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=128, blank=True, help_text='Optional access password')
    expires_at = models.DateTimeField(null=True, blank=True)
    activates_at = models.DateTimeField(null=True, blank=True)
    scan_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'QR Code'
        verbose_name_plural = 'QR Codes'

    def __str__(self):
        return f'{self.code} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.code.lower()
        if not self.code:
            self.code = generate_qr_code()
        super().save(*args, **kwargs)

    @property
    def public_path(self):
        return f'/qr/{self.code}'

    @property
    def public_url(self):
        base = getattr(settings, 'PUBLIC_SITE_URL', 'https://streetlabsafrica.org').rstrip('/')
        return f'{base}{self.public_path}'

    def is_currently_active(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.activates_at and now < self.activates_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True

    def resolve_destination(self):
        if self.destination_url:
            return self.destination_url
        obj = self.destination_object
        if obj is None:
            return None
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        if self.destination_type == self.DestinationType.PROFILE and hasattr(obj, 'username'):
            return f'/profiles/{obj.username}'
        if hasattr(obj, 'slug'):
            type_map = {
                self.DestinationType.PROJECT: 'projects',
                self.DestinationType.EVENT: 'events',
                self.DestinationType.PRODUCT: 'products',
                self.DestinationType.ORGANIZATION: 'organizations',
            }
            prefix = type_map.get(self.destination_type)
            if prefix:
                return f'/{prefix}/{obj.slug}'
        return None


class QRCodeLink(models.Model):
    class Icon(models.TextChoices):
        WEBSITE = 'website', 'Website'
        PROFILE = 'profile', 'Profile'
        LINKEDIN = 'linkedin', 'LinkedIn'
        EMAIL = 'email', 'Email'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        LOCATION = 'location', 'Location'
        MEETING = 'meeting', 'Book Meeting'
        PORTFOLIO = 'portfolio', 'Portfolio'
        CONTACT = 'contact', 'Download Contact'
        INSTAGRAM = 'instagram', 'Instagram'
        YOUTUBE = 'youtube', 'YouTube'
        TWITTER = 'twitter', 'X / Twitter'
        GITHUB = 'github', 'GitHub'
        PHONE = 'phone', 'Phone'
        CUSTOM = 'custom', 'Custom'

    qr = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=120)
    icon = models.CharField(max_length=40, choices=Icon.choices, default=Icon.CUSTOM)
    url = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.qr.code}: {self.label}'


class QRCodeAnalytics(models.Model):
    qr = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='scans')
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=120, blank=True)
    device = models.CharField(max_length=80, blank=True)
    browser = models.CharField(max_length=80, blank=True)
    os = models.CharField(max_length=80, blank=True)
    referrer = models.CharField(max_length=500, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_returning = models.BooleanField(default=False)
    link_clicked = models.ForeignKey(
        QRCodeLink,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='analytics',
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'QR code analytics'

    def __str__(self):
        return f'{self.qr.code} @ {self.timestamp}'
