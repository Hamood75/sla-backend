from django.conf import settings
from django.db import models
from django.utils.text import slugify


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    username = models.SlugField(unique=True, help_text='Public profile slug, e.g. hamood')
    display_name = models.CharField(max_length=160)
    position = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=160, blank=True)
    meeting_url = models.URLField(blank=True, help_text='Calendly or booking link')
    vcard_enabled = models.BooleanField(default=True)
    theme_primary = models.CharField(max_length=20, default='#ff6a00')
    theme_secondary = models.CharField(max_length=20, default='#0a1f44')
    is_public = models.BooleanField(default=True)
    department = models.ForeignKey(
        'accounts.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='profiles',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.username and self.display_name:
            self.username = slugify(self.display_name)
        super().save(*args, **kwargs)


class ProfileSocialLink(models.Model):
    class Platform(models.TextChoices):
        LINKEDIN = 'linkedin', 'LinkedIn'
        TWITTER = 'twitter', 'X / Twitter'
        GITHUB = 'github', 'GitHub'
        INSTAGRAM = 'instagram', 'Instagram'
        YOUTUBE = 'youtube', 'YouTube'
        FACEBOOK = 'facebook', 'Facebook'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'Email'
        WEBSITE = 'website', 'Website'
        OTHER = 'other', 'Other'

    profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=40, choices=Platform.choices)
    label = models.CharField(max_length=80, blank=True)
    url = models.URLField()
    icon = models.CharField(max_length=40, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.profile.username} — {self.platform}'


class ProfileProject(models.Model):
    profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='featured_projects')
    project = models.ForeignKey('cms.Project', on_delete=models.CASCADE, related_name='featured_on_profiles')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('profile', 'project')

    def __str__(self):
        return f'{self.profile.username} → {self.project.title}'
