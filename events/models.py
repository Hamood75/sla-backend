import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ExpoEvent(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    tagline = models.TextField()
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue_name = models.CharField(max_length=255)
    venue_address = models.TextField()
    venue_lat = models.FloatField(null=True, blank=True)
    venue_lng = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = 'events'
        ordering = ['-year']

    def __str__(self):
        return self.title


class ExpoEventHeroImage(TimeStampedModel):
    """Hero images for an ExpoEvent, stored in a separate table for easy management."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='hero_images'
    )
    image = models.ImageField(upload_to='events/heroes/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'event_hero_images'
        ordering = ['order', 'id']


class EventStat(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='stats'
    )
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'event_stats'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.label}: {self.value}'


class FocusArea(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='focus_areas'
    )
    num = models.CharField(max_length=10)
    title = models.CharField(max_length=150)
    description = models.TextField()
    accent_color = models.CharField(max_length=30)
    badge_color = models.CharField(max_length=30)
    image = models.ImageField(upload_to='events/focus-areas/', blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'focus_areas'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.num} - {self.title}'


class Partner(TimeStampedModel):
    class Tier(models.TextChoices):
        HOST = 'HOST', 'Host'
        LEAD_PARTNER = 'LEAD_PARTNER', 'Lead Partner'
        PARTNER = 'PARTNER', 'Partner'
        MEDIA = 'MEDIA', 'Media'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='partners'
    )
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='events/logos/', blank=True)
    tier = models.CharField(
        max_length=20, choices=Tier.choices, default=Tier.PARTNER
    )
    website_url = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'partners'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class ExpoVillage(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='villages'
    )
    slug = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    hall = models.CharField(max_length=150)
    emoji = models.CharField(max_length=20)
    theme_color = models.CharField(max_length=30)
    tagline = models.TextField()
    description = models.TextField()
    hero_image = models.ImageField(upload_to='events/villages/', blank=True)
    why_visit = models.TextField(blank=True, default='')
    stats = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'expo_villages'
        unique_together = [['event', 'slug']]
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class VillageBooth(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    village = models.ForeignKey(
        ExpoVillage, on_delete=models.CASCADE, related_name='booths'
    )
    name = models.CharField(max_length=200)
    org = models.CharField(max_length=200)
    booth_number = models.CharField(max_length=50)
    tag = models.CharField(max_length=50)
    description = models.TextField()
    live_demo = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    logo = models.ImageField(upload_to='events/booth-logos/', blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'village_booths'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.name} ({self.booth_number})'


class VillageSchedule(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    village = models.ForeignKey(
        ExpoVillage, on_delete=models.CASCADE, related_name='schedules'
    )
    time = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    presenter = models.CharField(max_length=200)
    booth_or_stage = models.CharField(max_length=100)
    day_number = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'village_schedules'
        ordering = ['day_number', 'order', 'id']

    def __str__(self):
        return f'{self.time} - {self.title}'


class VillageGallery(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    village = models.ForeignKey(
        ExpoVillage, on_delete=models.CASCADE, related_name='galleries'
    )
    image = models.ImageField(upload_to='events/gallery/', blank=True)
    title = models.CharField(max_length=200)
    caption = models.TextField()
    edition_year = models.PositiveIntegerField(default=2026)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'village_galleries'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class VillageHighlight(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    village = models.ForeignKey(
        ExpoVillage, on_delete=models.CASCADE, related_name='highlights'
    )
    icon = models.CharField(max_length=50)
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'village_highlights'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class BoothApplication(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        ALLOCATED = 'ALLOCATED', 'Allocated'
        REJECTED = 'REJECTED', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_no = models.CharField(max_length=50, unique=True, blank=True)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='booth_applications'
    )
    village = models.ForeignKey(
        ExpoVillage, on_delete=models.CASCADE, related_name='booth_applications'
    )
    company_name = models.CharField(max_length=200)
    company_website = models.TextField(blank=True)
    company_sector = models.CharField(max_length=100, blank=True)
    booth_package = models.CharField(max_length=100)
    showcase_title = models.CharField(max_length=255)
    showcase_desc = models.TextField()
    tech_requirements = ArrayField(
        models.CharField(max_length=200), default=list, blank=True
    )
    co_exhibitors = models.TextField(blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    job_title = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING_REVIEW
    )
    assigned_booth_no = models.CharField(max_length=50, blank=True)
    admin_notes = models.TextField(blank=True)
    agree_terms = models.BooleanField(default=True)

    class Meta:
        db_table = 'booth_applications'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_no:
            self.reference_no = f'TZ-DPI-BOOTH-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.reference_no} - {self.company_name}'


class Registration(TimeStampedModel):
    class RegType(models.TextChoices):
        GUEST = 'GUEST', 'Guest'
        SPEAKER = 'SPEAKER', 'Speaker'
        VOLUNTEER = 'VOLUNTEER', 'Volunteer'

    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        WAITLIST = 'WAITLIST', 'Waitlist'
        REJECTED = 'REJECTED', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_no = models.CharField(max_length=50, unique=True, blank=True)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='registrations'
    )
    type = models.CharField(max_length=20, choices=RegType.choices)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    organization = models.CharField(max_length=200, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CONFIRMED
    )
    badge_code = models.CharField(max_length=100, unique=True, blank=True)
    agree_terms = models.BooleanField(default=True)

    class Meta:
        db_table = 'registrations'
        unique_together = [['event', 'email', 'type']]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_no:
            self.reference_no = f'TZ-DPI-{self.type[:3].upper()}-{uuid.uuid4().hex[:8].upper()}'
        if not self.badge_code:
            self.badge_code = f'QR-{self.reference_no}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.reference_no} - {self.first_name} {self.last_name}'

    def create_speaker(self):
        """Create a Speaker record from a SPEAKER registration if one does not exist."""
        if self.type != self.RegType.SPEAKER:
            return None
        name = f'{self.first_name or ""} {self.last_name or ""}'.strip()
        speaker = Speaker.objects.filter(event=self.event, name=name).first()
        if speaker:
            return speaker
        initials = (self.first_name[:1] + self.last_name[:1]).upper() if self.first_name and self.last_name else ''
        extra = self.extra_data or {}
        return Speaker.objects.create(
            event=self.event,
            name=name,
            title=extra.get('talk_title', '') or self.organization or '',
            org=self.organization or '',
            initials=initials,
            color='#2563EB',
            accent_light='#DBEAFE',
            bio=extra.get('speaker_bio', '') or extra.get('talk_abstract', ''),
            is_confirmed=True,
            order=Speaker.objects.filter(event=self.event).count() + 1,
        )


class Speaker(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='speakers'
    )
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    org = models.CharField(max_length=200)
    initials = models.CharField(max_length=10)
    color = models.CharField(max_length=30)
    accent_light = models.CharField(max_length=30)
    photo = models.ImageField(upload_to='events/speakers/', blank=True)
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_confirmed = models.BooleanField(default=True)

    class Meta:
        db_table = 'speakers'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class Session(TimeStampedModel):
    class Type(models.TextChoices):
        KEYNOTE = 'KEYNOTE', 'Keynote'
        PANEL = 'PANEL', 'Panel'
        WORKSHOP = 'WORKSHOP', 'Workshop'
        BREAK = 'BREAK', 'Break'
        EXHIBITION = 'EXHIBITION', 'Exhibition'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, on_delete=models.CASCADE, related_name='sessions'
    )
    day_number = models.PositiveIntegerField(default=1)
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=Type.choices)
    speaker = models.ForeignKey(
        Speaker, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='sessions'
    )
    speaker_text = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'sessions'
        ordering = ['day_number', 'order', 'id']

    def __str__(self):
        return self.title


class MediaAsset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        ExpoEvent, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='media_assets'
    )
    original_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    folder = models.CharField(max_length=50)
    file = models.FileField(upload_to='events/media/', blank=True)
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True)
    alt_text = models.TextField(blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'media_assets'
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name
