from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(TimeStampedModel):
    org_name = models.CharField(max_length=200, default='Street Digital Labs Africa')
    org_short_name = models.CharField(max_length=120, default='Street Labs')
    tagline = models.CharField(max_length=200, default='Inclusion for All!')
    logo = models.ImageField(upload_to='cms/brand/', blank=True, null=True)
    logo_alt = models.CharField(max_length=200, blank=True)
    favicon = models.ImageField(upload_to='cms/brand/', blank=True, null=True)
    primary_color = models.CharField(max_length=20, default='#ff6a00')
    secondary_color = models.CharField(max_length=20, default='#0a7a3d')
    navy_color = models.CharField(max_length=20, default='#0a1f44')
    social_handle = models.CharField(max_length=80, default='@streetlabsafrica')
    website_url = models.URLField(default='https://streetlabsafrica.org')
    copyright_name = models.CharField(max_length=200, default='Street Digital Labs Africa')
    footer_credit = models.CharField(max_length=200, default='Made with love for Africa')
    response_sla_hours = models.PositiveIntegerField(default=24)
    address = models.CharField(max_length=255, default='Morogoro, Tanzania')
    phone = models.CharField(max_length=40, default='+255 800 123 456')
    email = models.EmailField(default='info@streetlabsafrica.org')
    website_display = models.CharField(max_length=120, default='streetlabsafrica.org')

    class Meta:
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return self.org_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AnnouncementBar(TimeStampedModel):
    class CTAAction(models.TextChoices):
        OPEN_DONATE = 'open_donate', 'Open Donate'
        URL = 'url', 'External URL'

    is_active = models.BooleanField(default=True)
    message = models.CharField(max_length=300, default='Help us empower 10,000 more youth this year —')
    cta_label = models.CharField(max_length=80, default='Donate Now →')
    cta_action = models.CharField(max_length=20, choices=CTAAction.choices, default=CTAAction.OPEN_DONATE)
    cta_url = models.URLField(blank=True)
    dismissible = models.BooleanField(default=True)

    def __str__(self):
        return self.message[:60]


class NavItem(TimeStampedModel):
    class Placement(models.TextChoices):
        HEADER = 'header', 'Header'
        FOOTER = 'footer', 'Footer'
        BOTH = 'both', 'Both'

    label = models.CharField(max_length=80)
    href = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    placement = models.CharField(max_length=20, choices=Placement.choices, default=Placement.BOTH)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label


class HeroSection(TimeStampedModel):
    class CTAAction(models.TextChoices):
        OPEN_DONATE = 'open_donate', 'Open Donate'
        URL = 'url', 'URL'
        ANCHOR = 'anchor', 'Anchor'

    background_video = models.FileField(upload_to='cms/hero/', blank=True, null=True)
    video_poster = models.ImageField(upload_to='cms/hero/', blank=True, null=True)
    title_line_1 = models.CharField(max_length=200, default='Empowering Africa')
    title_accent = models.CharField(max_length=200, default='One Skill at a Time.')
    description = models.TextField(blank=True)
    primary_cta_label = models.CharField(max_length=80, default='Donate Now')
    primary_cta_action = models.CharField(max_length=20, choices=CTAAction.choices, default=CTAAction.OPEN_DONATE)
    primary_cta_href = models.CharField(max_length=255, blank=True)
    secondary_cta_label = models.CharField(max_length=80, default='Explore Programs ↓')
    secondary_cta_href = models.CharField(max_length=255, default='#services')
    impact_label = models.CharField(max_length=80, default='OUR IMPACT')
    impact_badge = models.CharField(max_length=120, default='Best EdTech 2024')
    impact_title = models.CharField(max_length=200, default='Digital Skills for Everyone')
    impact_subtitle = models.CharField(max_length=255, default='Empowering communities. Building futures.')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Hero sections'

    def __str__(self):
        return f'{self.title_line_1} {self.title_accent}'


class HeroTag(models.Model):
    hero = models.ForeignKey(HeroSection, on_delete=models.CASCADE, related_name='tags')
    label = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label


class HeroProgressBar(models.Model):
    class ColorVariant(models.TextChoices):
        ORANGE = 'orange', 'Orange'
        GREEN = 'green', 'Green'

    hero = models.ForeignKey(HeroSection, on_delete=models.CASCADE, related_name='progress_bars')
    label = models.CharField(max_length=120)
    display_value = models.CharField(max_length=40)
    percent = models.PositiveIntegerField(default=0)
    color_variant = models.CharField(max_length=20, choices=ColorVariant.choices, default=ColorVariant.ORANGE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label


class ImpactStat(TimeStampedModel):
    class Placement(models.TextChoices):
        HERO = 'hero', 'Hero'
        ABOUT = 'about', 'About'
        GALLERY = 'gallery', 'Gallery'

    value = models.CharField(max_length=40)
    label = models.CharField(max_length=120)
    placement = models.CharField(max_length=20, choices=Placement.choices)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['placement', 'order', 'id']

    def __str__(self):
        return f'{self.value} — {self.label} ({self.placement})'


class GallerySection(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default='Our Community In Action')
    title = models.CharField(max_length=200, default='Hands On at SLA')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class GalleryImage(TimeStampedModel):
    section = models.ForeignKey(GallerySection, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cms/gallery/')
    alt = models.CharField(max_length=200, blank=True)
    label = models.CharField(max_length=120, blank=True)
    accent_color = models.CharField(max_length=20, default='#ff6a00')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label or self.alt or f'Image {self.pk}'


class AboutSection(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default='Who We Are')
    title = models.CharField(max_length=200, default='About Street Labs')
    description = models.TextField(blank=True)
    mission_title = models.CharField(max_length=120, default='Our Mission')
    mission_text = models.TextField(blank=True)
    mission_icon = models.CharField(max_length=20, default='🎯')
    vision_title = models.CharField(max_length=120, default='Our Vision')
    vision_text = models.TextField(blank=True)
    vision_icon = models.CharField(max_length=20, default='🌍')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class BrandValue(TimeStampedModel):
    emoji = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#ff6a00')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Program(TimeStampedModel):
    emoji = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    tag = models.CharField(max_length=80, blank=True)
    tag_color = models.CharField(max_length=20, default='#ff6a00')
    learn_more_href = models.CharField(max_length=255, default='#contact')
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class OrgChartNode(TimeStampedModel):
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=120, blank=True)
    icon = models.CharField(max_length=20, blank=True)
    level = models.PositiveIntegerField(default=1)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )
    color = models.CharField(max_length=20, default='#0a1f44')
    accent_color = models.CharField(max_length=20, default='#ff6a00')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'order', 'id']

    def __str__(self):
        return self.title


class TeamMember(TimeStampedModel):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=160)
    bio = models.TextField(blank=True)
    initials = models.CharField(max_length=8, blank=True)
    photo = models.ImageField(upload_to='cms/team/', blank=True, null=True)
    avatar_color = models.CharField(max_length=20, default='#ff6a00')
    org_role = models.ForeignKey(
        OrgChartNode,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_members',
    )
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    accepts_meetings = models.BooleanField(
        default=True,
        help_text='Show Book a Meeting on the public team preview',
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class MeetingRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        DECLINED = 'declined', 'Declined'
        CANCELLED = 'cancelled', 'Cancelled'

    official = models.ForeignKey(
        TeamMember,
        on_delete=models.CASCADE,
        related_name='meeting_requests',
    )
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    organization = models.CharField(max_length=160, blank=True)
    preferred_at = models.DateTimeField(help_text='Requested meeting date/time')
    topic = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} → {self.official.name} ({self.status})'


class SocialLink(TimeStampedModel):
    class Platform(models.TextChoices):
        FACEBOOK = 'facebook', 'Facebook'
        TWITTER = 'twitter', 'X / Twitter'
        LINKEDIN = 'linkedin', 'LinkedIn'
        YOUTUBE = 'youtube', 'YouTube'
        INSTAGRAM = 'instagram', 'Instagram'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        OTHER = 'other', 'Other'

    platform = models.CharField(max_length=40, choices=Platform.choices)
    url = models.URLField()
    icon_label = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)
    show_in_contact = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.platform


class ContactMessage(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        READ = 'read', 'Read'
        REPLIED = 'replied', 'Replied'

    name = models.CharField(max_length=160)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    admin_reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contact_replies',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.subject or self.message[:40]}'


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=80, default='footer')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class DonationTier(TimeStampedModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    label = models.CharField(max_length=40)
    impact = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=8, default='USD')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'amount']
        verbose_name_plural = 'Donation tiers'

    def __str__(self):
        return self.label


class PaymentMethod(TimeStampedModel):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=40, blank=True)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=20, default='#0a1f44')
    requires_phone = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class DonateModalCopy(TimeStampedModel):
    title = models.CharField(max_length=160, default='Make a Donation')
    subtitle = models.CharField(
        max_length=255,
        default="Your gift empowers Africa's next digital generation.",
    )
    country_dial_code = models.CharField(max_length=10, default='+255')
    country_flag_label = models.CharField(max_length=20, default='🇹🇿')
    gateway_notice = models.TextField(blank=True)
    secure_note = models.CharField(max_length=255, default='Secure 256-bit SSL encryption')
    success_title = models.CharField(max_length=120, default='Thank You!')
    success_body_template = models.TextField(
        default='Your donation of {amount} {currency} has been received.',
    )

    class Meta:
        verbose_name_plural = 'Donate modal copy'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Donation(TimeStampedModel):
    class DonationType(models.TextChoices):
        ONCE = 'once', 'One-time'
        MONTHLY = 'monthly', 'Monthly'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='USD')
    donation_type = models.CharField(max_length=20, choices=DonationType.choices, default=DonationType.ONCE)
    payment_method = models.ForeignKey(
        PaymentMethod,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='donations',
    )
    phone = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    external_reference = models.CharField(max_length=120, blank=True)
    transaction_reference = models.CharField(max_length=120, blank=True, unique=True)
    raw_gateway_response = models.JSONField(default=dict, blank=True)
    donor_name = models.CharField(max_length=160, blank=True)
    donor_email = models.EmailField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.transaction_reference or f'Donation {self.pk}'


class Project(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='cms/projects/', blank=True, null=True)
    website_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Event(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    registration_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to='cms/events/', blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-starts_at', 'title']

    def __str__(self):
        return self.title


class Product(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='cms/products/', blank=True, null=True)
    website_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
