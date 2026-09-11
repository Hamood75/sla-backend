import base64
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers

from .models import (
    BoothApplication,
    EventStat,
    ExpoEvent,
    ExpoEventHeroImage,
    ExpoVillage,
    FocusArea,
    MediaAsset,
    Partner,
    Registration,
    Session,
    Speaker,
    VillageBooth,
    VillageGallery,
    VillageHighlight,
    VillageSchedule,
)


class AbsoluteURLImageField(serializers.ImageField):
    """ImageField that accepts base64 data URIs on input and returns absolute URLs in responses."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            header, _, b64_content = data.partition(',')
            mime_type = header.split(';')[0].split(':')[1] if ':' in header else 'image/png'
            ext = mime_type.split('/')[-1].split('+')[0]
            name = f'upload_{uuid.uuid4().hex[:8]}.{ext}'
            decoded = base64.b64decode(b64_content)
            return ContentFile(decoded, name=name)
        return super().to_internal_value(data)

    def to_representation(self, value):
        if not value:
            return ''
        url = value.url
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class AbsoluteURLFileField(serializers.FileField):
    """FileField that accepts base64 data URIs on input and returns absolute URLs in responses."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            header, _, b64_content = data.partition(',')
            mime_type = header.split(';')[0].split(':')[1] if ':' in header else 'application/octet-stream'
            ext = mime_type.split('/')[-1].split('+')[0]
            name = f'upload_{uuid.uuid4().hex[:8]}.{ext}'
            decoded = base64.b64decode(b64_content)
            return ContentFile(decoded, name=name)
        return super().to_internal_value(data)

    def to_representation(self, value):
        if not value:
            return None
        url = value.url
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class EventStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStat
        fields = ['id', 'event', 'label', 'value', 'order', 'created_at', 'updated_at']


class AdminEventStatSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for EventStat (snake_case for admin forms)."""
    class Meta:
        model = EventStat
        fields = ['id', 'event', 'label', 'value', 'order', 'created_at', 'updated_at']


class FocusAreaSerializer(serializers.ModelSerializer):
    """Public-facing serializer with camelCase output matching frontend docs."""
    accentColor = serializers.CharField(source='accent_color')
    badgeColor = serializers.CharField(source='badge_color')
    img = AbsoluteURLImageField(source='image')
    desc = serializers.CharField(source='description')

    class Meta:
        model = FocusArea
        fields = ['id', 'num', 'title', 'desc', 'accentColor', 'badgeColor', 'img']


class AdminFocusAreaSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for FocusArea (snake_case for admin forms)."""
    image = AbsoluteURLImageField(required=False, allow_null=True)

    class Meta:
        model = FocusArea
        fields = [
            'id', 'event', 'num', 'title', 'description',
            'accent_color', 'badge_color', 'image', 'order',
            'created_at', 'updated_at',
        ]


class PartnerSerializer(serializers.ModelSerializer):
    """Public-facing serializer with camelCase output matching frontend docs."""
    logo = AbsoluteURLImageField()

    class Meta:
        model = Partner
        fields = ['id', 'name', 'logo']


class AdminPartnerSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for Partner (snake_case for admin forms)."""
    logo = AbsoluteURLImageField(required=False, allow_null=True)

    class Meta:
        model = Partner
        fields = ['id', 'event', 'name', 'logo', 'tier', 'website_url', 'order', 'created_at', 'updated_at']


class HeroImageSerializer(serializers.ModelSerializer):
    """Serializer for ExpoEventHeroImage — returns absolute URL for image."""
    image = AbsoluteURLImageField(required=False, allow_null=True)

    class Meta:
        model = ExpoEventHeroImage
        fields = ['id', 'event', 'image', 'order', 'created_at', 'updated_at']
        extra_kwargs = {'event': {'write_only': True}}


class ExpoEventSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for ExpoEvent (snake_case for admin forms)."""
    hero_images = HeroImageSerializer(many=True, read_only=True)

    class Meta:
        model = ExpoEvent
        fields = [
            'id', 'year', 'title', 'tagline', 'description',
            'start_date', 'end_date', 'venue_name', 'venue_address',
            'venue_lat', 'venue_lng', 'hero_images',
            'is_active', 'is_published', 'created_at', 'updated_at',
        ]


class EventEditionSerializer(serializers.Serializer):
    """Public serializer for listing all event editions/years."""
    id = serializers.UUIDField()
    year = serializers.IntegerField()
    title = serializers.CharField()
    tagline = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    venue_name = serializers.CharField()
    is_current = serializers.BooleanField()


class AdminEventEditionSerializer(serializers.Serializer):
    """Admin serializer for listing all event years with status flags."""
    id = serializers.UUIDField()
    year = serializers.IntegerField()
    title = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    is_published = serializers.BooleanField()
    is_current = serializers.BooleanField()


class LandingEventSerializer(serializers.ModelSerializer):
    """Public event serializer with camelCase output for landing page."""
    startDate = serializers.DateTimeField(source='start_date')
    endDate = serializers.DateTimeField(source='end_date')
    heroImages = HeroImageSerializer(many=True, source='hero_images', read_only=True)
    venue = serializers.SerializerMethodField()

    class Meta:
        model = ExpoEvent
        fields = ['id', 'year', 'title', 'tagline', 'description', 'startDate', 'endDate', 'venue', 'heroImages']

    def get_venue(self, obj):
        return {
            'name': obj.venue_name,
            'address': obj.venue_address,
            'latitude': obj.venue_lat,
            'longitude': obj.venue_lng,
        }


class AdminEventDetailSerializer(serializers.ModelSerializer):
    """Admin detail serializer with all nested sub-items for full event management."""
    hero_images = HeroImageSerializer(many=True, read_only=True)
    stats = AdminEventStatSerializer(many=True, read_only=True)
    focus_areas = AdminFocusAreaSerializer(many=True, read_only=True)
    partners = AdminPartnerSerializer(many=True, read_only=True)
    villages = serializers.SerializerMethodField()
    speakers = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    booth_applications = serializers.SerializerMethodField()
    registrations = serializers.SerializerMethodField()

    class Meta:
        model = ExpoEvent
        fields = [
            'id', 'year', 'title', 'tagline', 'description',
            'start_date', 'end_date', 'venue_name', 'venue_address',
            'venue_lat', 'venue_lng', 'hero_images',
            'is_active', 'is_published', 'created_at', 'updated_at',
            'stats', 'focus_areas', 'partners',
            'villages', 'speakers', 'sessions',
            'booth_applications', 'registrations',
        ]

    def get_villages(self, obj):
        qs = obj.villages.order_by('order')
        return ExpoVillageListSerializer(qs, many=True, context=self.context).data

    def get_speakers(self, obj):
        qs = obj.speakers.order_by('order')
        return SpeakerSerializer(qs, many=True, context=self.context).data

    def get_sessions(self, obj):
        qs = obj.sessions.order_by('day_number', 'order')
        return SessionSerializer(qs, many=True, context=self.context).data

    def get_booth_applications(self, obj):
        qs = obj.booth_applications.order_by('-created_at')
        return BoothApplicationSerializer(qs, many=True, context=self.context).data

    def get_registrations(self, obj):
        qs = obj.registrations.order_by('-created_at')
        return RegistrationSerializer(qs, many=True, context=self.context).data


class VillageBoothSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for VillageBooth (snake_case)."""
    logo = AbsoluteURLImageField(required=False, allow_null=True)

    class Meta:
        model = VillageBooth
        fields = [
            'id', 'village', 'name', 'org', 'booth_number', 'tag',
            'description', 'live_demo', 'website_url', 'logo',
            'is_featured', 'order',
        ]


class PublicVillageBoothSerializer(serializers.ModelSerializer):
    """Public serializer with camelCase output for village detail."""
    boothNo = serializers.CharField(source='booth_number')
    liveDemo = serializers.CharField(source='live_demo')
    websiteUrl = serializers.CharField(source='website_url')
    logoUrl = AbsoluteURLImageField(source='logo')
    isFeatured = serializers.BooleanField(source='is_featured')
    desc = serializers.CharField(source='description')

    class Meta:
        model = VillageBooth
        fields = ['id', 'name', 'org', 'boothNo', 'tag', 'desc', 'liveDemo', 'websiteUrl', 'logoUrl', 'isFeatured']


class VillageScheduleSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for VillageSchedule (snake_case)."""
    class Meta:
        model = VillageSchedule
        fields = [
            'id', 'village', 'time', 'title', 'presenter',
            'booth_or_stage', 'day_number', 'order',
        ]


class PublicVillageScheduleSerializer(serializers.ModelSerializer):
    """Public serializer with camelCase output for village detail."""
    booth = serializers.CharField(source='booth_or_stage')

    class Meta:
        model = VillageSchedule
        fields = ['id', 'time', 'title', 'presenter', 'booth']


class VillageGallerySerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for VillageGallery (snake_case)."""
    image = AbsoluteURLImageField(required=False, allow_null=True)

    class Meta:
        model = VillageGallery
        fields = ['id', 'village', 'image', 'title', 'caption', 'edition_year', 'order']


class PublicVillageGallerySerializer(serializers.ModelSerializer):
    """Public serializer with camelCase output for village detail."""
    url = AbsoluteURLImageField(source='image')

    class Meta:
        model = VillageGallery
        fields = ['id', 'url', 'title', 'caption']


class VillageHighlightSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for VillageHighlight (snake_case)."""
    class Meta:
        model = VillageHighlight
        fields = ['id', 'village', 'icon', 'title', 'description', 'order']


class PublicVillageHighlightSerializer(serializers.ModelSerializer):
    """Public serializer for village highlights."""
    class Meta:
        model = VillageHighlight
        fields = ['id', 'icon', 'title', 'description', 'order']


class ExpoVillageListSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for village list (snake_case)."""
    booths_count = serializers.SerializerMethodField()
    demos_count = serializers.SerializerMethodField()

    hero_image = AbsoluteURLImageField(required=False, allow_null=True)

    class Meta:
        model = ExpoVillage
        fields = [
            'id', 'event', 'slug', 'name', 'hall', 'emoji', 'theme_color',
            'tagline', 'description', 'hero_image',
            'booths_count', 'demos_count', 'order',
        ]
        read_only_fields = ['booths_count', 'demos_count']

    def get_booths_count(self, obj):
        return obj.booths.count()

    def get_demos_count(self, obj):
        return obj.schedules.count()


class PublicVillageListSerializer(serializers.ModelSerializer):
    """Public village list serializer with camelCase output matching frontend docs."""
    themeColor = serializers.CharField(source='theme_color')
    heroImage = AbsoluteURLImageField(source='hero_image')
    boothsCount = serializers.SerializerMethodField()
    demosCount = serializers.SerializerMethodField()
    desc = serializers.CharField(source='description')

    class Meta:
        model = ExpoVillage
        fields = ['id', 'slug', 'name', 'hall', 'emoji', 'themeColor', 'tagline', 'desc', 'heroImage', 'boothsCount', 'demosCount', 'order']

    def get_boothsCount(self, obj):
        return obj.booths.count()

    def get_demosCount(self, obj):
        return obj.schedules.count()


class ExpoVillageDetailSerializer(serializers.ModelSerializer):
    """Admin detail serializer for village (snake_case with nested)."""
    stats = serializers.JSONField(required=False)
    hero_image = AbsoluteURLImageField(required=False, allow_null=True)
    booths = VillageBoothSerializer(many=True, read_only=True)
    schedule = VillageScheduleSerializer(
        many=True, read_only=True, source='schedules'
    )
    gallery = VillageGallerySerializer(
        many=True, read_only=True, source='galleries'
    )
    highlights = VillageHighlightSerializer(many=True, read_only=True)

    class Meta:
        model = ExpoVillage
        fields = [
            'id', 'event', 'slug', 'name', 'hall', 'emoji', 'theme_color',
            'tagline', 'description', 'why_visit', 'highlights', 'hero_image', 'stats',
            'booths', 'schedule', 'gallery', 'order',
        ]
        read_only_fields = ['booths', 'schedule', 'gallery', 'highlights']


class PublicVillageDetailSerializer(serializers.ModelSerializer):
    """Public village detail serializer with camelCase output matching frontend docs."""
    themeColor = serializers.CharField(source='theme_color')
    heroImage = AbsoluteURLImageField(source='hero_image')
    whyVisit = serializers.CharField(source='why_visit')
    keyHighlights = PublicVillageHighlightSerializer(
        many=True, read_only=True, source='highlights'
    )
    stats = serializers.JSONField(required=False)
    booths = PublicVillageBoothSerializer(many=True, read_only=True)
    schedule = PublicVillageScheduleSerializer(
        many=True, read_only=True, source='schedules'
    )
    gallery = PublicVillageGallerySerializer(
        many=True, read_only=True, source='galleries'
    )

    class Meta:
        model = ExpoVillage
        fields = [
            'id', 'slug', 'name', 'hall', 'emoji', 'themeColor',
            'tagline', 'description', 'whyVisit', 'keyHighlights', 'heroImage', 'stats',
            'booths', 'schedule', 'gallery', 'order',
        ]


class SpeakerSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for Speaker (snake_case)."""
    photo = AbsoluteURLImageField(required=False, allow_null=True)
    is_approved = serializers.BooleanField(source='is_confirmed', read_only=True)

    class Meta:
        model = Speaker
        fields = [
            'id', 'event', 'name', 'title', 'org', 'initials',
            'color', 'accent_light', 'photo', 'bio', 'order', 'is_confirmed',
            'is_approved',
        ]


class PublicSpeakerSerializer(serializers.ModelSerializer):
    """Public speaker serializer with camelCase output matching frontend docs."""
    accentLight = serializers.CharField(source='accent_light')
    isApproved = serializers.BooleanField(source='is_confirmed', read_only=True)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Speaker
        fields = ['id', 'name', 'title', 'org', 'initials', 'color', 'accentLight', 'isApproved', 'photo', 'bio', 'order']

    def get_photo(self, obj):
        if obj.photo:
            request = self.context.get('request')
            url = obj.photo.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        initials = obj.initials or ''.join([n[:1] for n in obj.name.split()[:2] if n]).upper()
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">'
            f'<rect width="200" height="200" fill="{obj.color}"/>'
            f'<text x="50%" y="50%" font-size="80" font-family="sans-serif" fill="white" '
            f'text-anchor="middle" dominant-baseline="central">{initials}</text>'
            f'</svg>'
        )
        b64 = base64.b64encode(svg.encode()).decode()
        return f'data:image/svg+xml;base64,{b64}'


class SessionSerializer(serializers.ModelSerializer):
    """Admin CRUD serializer for Session (snake_case)."""
    speaker = SpeakerSerializer(read_only=True)
    speaker_id = serializers.PrimaryKeyRelatedField(
        queryset=Speaker.objects.all(), source='speaker', required=False, allow_null=True
    )

    class Meta:
        model = Session
        fields = [
            'id', 'event', 'day_number', 'start_time', 'end_time',
            'title', 'type', 'speaker', 'speaker_id', 'speaker_text', 'location', 'order',
        ]
        read_only_fields = ['speaker']


class PublicSessionSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    speaker = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'time', 'title', 'type', 'speaker', 'location']

    def get_time(self, obj):
        return f'{obj.start_time} – {obj.end_time}'

    def get_speaker(self, obj):
        if obj.speaker:
            return obj.speaker.name
        return obj.speaker_text or None


class BoothApplicationSerializer(serializers.ModelSerializer):
    reference_no = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BoothApplication
        fields = [
            'id', 'reference_no', 'event', 'village',
            'company_name', 'company_website', 'company_sector',
            'booth_package', 'showcase_title', 'showcase_desc',
            'tech_requirements', 'co_exhibitors',
            'first_name', 'last_name', 'email', 'phone',
            'job_title', 'country', 'status', 'assigned_booth_no',
            'admin_notes', 'agree_terms', 'created_at', 'updated_at',
        ]


class BoothApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothApplication
        fields = ['status', 'assigned_booth_no', 'admin_notes']


class RegistrationSerializer(serializers.ModelSerializer):
    reference_no = serializers.CharField(read_only=True)
    badge_code = serializers.CharField(read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id', 'reference_no', 'event', 'type',
            'first_name', 'last_name', 'email', 'phone', 'country',
            'organization', 'extra_data', 'status', 'badge_code',
            'agree_terms', 'created_at', 'updated_at',
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if (instance.status == Registration.Status.APPROVED
                and instance.type == Registration.RegType.SPEAKER):
            instance.create_speaker()
        return instance


class GuestRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=100)
    organization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    guest_category = serializers.CharField(max_length=100, required=False, allow_blank=True)
    dietary_reqs = serializers.CharField(max_length=200, required=False, allow_blank=True)
    agree_terms = serializers.BooleanField(default=True)

    def create(self, validated_data):
        event = self.context['event']
        extra = {
            'guest_category': validated_data.pop('guest_category', ''),
            'dietary_reqs': validated_data.pop('dietary_reqs', ''),
        }
        return Registration.objects.create(
            event=event,
            type=Registration.RegType.GUEST,
            extra_data=extra,
            **{k: v for k, v in validated_data.items() if k != 'agree_terms'},
            agree_terms=validated_data.get('agree_terms', True),
        )


class SpeakerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=100)
    organization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    talk_title = serializers.CharField(max_length=255)
    talk_abstract = serializers.CharField()
    speaker_bio = serializers.CharField()
    linked_in = serializers.URLField(required=False, allow_blank=True)
    previous_speaking = serializers.CharField(required=False, allow_blank=True)
    agree_terms = serializers.BooleanField(default=True)

    def create(self, validated_data):
        event = self.context['event']
        extra = {
            'talk_title': validated_data.pop('talk_title'),
            'talk_abstract': validated_data.pop('talk_abstract'),
            'speaker_bio': validated_data.pop('speaker_bio'),
            'linked_in': validated_data.pop('linked_in', ''),
            'previous_speaking': validated_data.pop('previous_speaking', ''),
        }
        return Registration.objects.create(
            event=event,
            type=Registration.RegType.SPEAKER,
            extra_data=extra,
            **{k: v for k, v in validated_data.items() if k not in ('agree_terms',)},
            agree_terms=validated_data.get('agree_terms', True),
        )


class VolunteerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=100)
    organization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    volunteer_role = serializers.CharField(max_length=100)
    availability = serializers.ListField(child=serializers.CharField(max_length=200))
    skills = serializers.CharField(required=False, allow_blank=True)
    motivation = serializers.CharField(required=False, allow_blank=True)
    agree_terms = serializers.BooleanField(default=True)

    def create(self, validated_data):
        event = self.context['event']
        extra = {
            'volunteer_role': validated_data.pop('volunteer_role'),
            'availability': validated_data.pop('availability'),
            'skills': validated_data.pop('skills', ''),
            'motivation': validated_data.pop('motivation', ''),
        }
        return Registration.objects.create(
            event=event,
            type=Registration.RegType.VOLUNTEER,
            extra_data=extra,
            **{k: v for k, v in validated_data.items() if k != 'agree_terms'},
            agree_terms=validated_data.get('agree_terms', True),
        )


class BoothPublicRegistrationSerializer(serializers.Serializer):
    selected_village = serializers.CharField(max_length=50)
    company_name = serializers.CharField(max_length=200)
    company_website = serializers.URLField(required=False, allow_blank=True)
    company_sector = serializers.CharField(max_length=100, required=False, allow_blank=True)
    booth_package = serializers.CharField(max_length=100)
    showcase_title = serializers.CharField(max_length=255)
    showcase_description = serializers.CharField()
    tech_requirements = serializers.ListField(
        child=serializers.CharField(max_length=200), default=list
    )
    co_exhibitors = serializers.CharField(required=False, allow_blank=True)
    contact = serializers.DictField()
    agree_terms = serializers.BooleanField(default=True)

    def create(self, validated_data):
        event = self.context['event']
        village_slug = validated_data.pop('selected_village')
        try:
            village = ExpoVillage.objects.get(event=event, slug=village_slug)
        except ExpoVillage.DoesNotExist:
            raise serializers.ValidationError(
                {'selected_village': 'Village not found for this event.'}
            )
        contact = validated_data.pop('contact', {})
        app = BoothApplication.objects.create(
            event=event,
            village=village,
            company_name=validated_data['company_name'],
            company_website=validated_data.get('company_website', ''),
            company_sector=validated_data.get('company_sector', ''),
            booth_package=validated_data['booth_package'],
            showcase_title=validated_data['showcase_title'],
            showcase_desc=validated_data['showcase_description'],
            tech_requirements=validated_data.get('tech_requirements', []),
            co_exhibitors=validated_data.get('co_exhibitors', ''),
            first_name=contact.get('first_name', ''),
            last_name=contact.get('last_name', ''),
            email=contact.get('email', ''),
            phone=contact.get('phone', ''),
            job_title=contact.get('job_title', ''),
            country=contact.get('country', ''),
            agree_terms=validated_data.get('agree_terms', True),
        )
        return app


class MediaAssetSerializer(serializers.ModelSerializer):
    """Serializer for MediaAsset with base64 file upload support."""
    file_base64 = serializers.CharField(write_only=True, required=False)
    file = AbsoluteURLFileField(read_only=True)
    thumbnail = AbsoluteURLImageField(read_only=True)
    altText = serializers.CharField(source='alt_text', required=False, allow_blank=True)
    eventId = serializers.PrimaryKeyRelatedField(
        source='event', queryset=ExpoEvent.objects.all(), required=False, allow_null=True
    )
    originalName = serializers.CharField(source='original_name', read_only=True)
    fileName = serializers.CharField(source='file_name', read_only=True)
    mimeType = serializers.CharField(source='mime_type', read_only=True)
    sizeBytes = serializers.IntegerField(source='size_bytes', read_only=True)
    alt_text_read = serializers.CharField(source='alt_text', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    dimensions = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            'id', 'event', 'eventId',
            'original_name', 'originalName', 'file_name', 'fileName',
            'mime_type', 'mimeType', 'size_bytes', 'sizeBytes',
            'folder', 'file', 'thumbnail',
            'alt_text', 'alt_text_read', 'altText',
            'width', 'height', 'dimensions',
            'created_at', 'createdAt',
            'file_base64',
        ]
        read_only_fields = [
            'id', 'original_name', 'file_name', 'mime_type',
            'size_bytes', 'file', 'thumbnail', 'width', 'height', 'created_at',
        ]

    def get_dimensions(self, obj):
        if obj.width and obj.height:
            return {'width': obj.width, 'height': obj.height}
        return None


# --- Public Response Serializers ---

class LandingPageResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = serializers.SerializerMethodField()

    def get_data(self, event):
        request = self.context.get('request')
        villages = event.villages.order_by('order')
        village_data = [{
            'id': str(v.id), 'name': v.name, 'slug': v.slug,
            'img': request.build_absolute_uri(v.hero_image.url) if v.hero_image and request else (v.hero_image.url if v.hero_image else ''),
            'desc': v.description,
            'booths': v.booths.count(), 'demos': v.schedules.count(),
            'order': v.order,
        } for v in villages]

        gallery = [{
            'id': str(g.id),
            'url': request.build_absolute_uri(g.image.url) if g.image and request else (g.image.url if g.image else ''),
            'title': g.title,
            'layout': 'standard',
        } for g in VillageGallery.objects.filter(village__event=event)[:4]]

        return {
            'event': LandingEventSerializer(event, context=self.context).data,
            'stats': list(event.stats.values('label', 'value')),
            'villages': village_data,
            'gallery': gallery,
            'focusAreas': FocusAreaSerializer(
                event.focus_areas.all(), many=True, context=self.context
            ).data,
            'partners': PartnerSerializer(
                event.partners.all(), many=True, context=self.context
            ).data,
            'featuredSpeakers': PublicSpeakerSerializer(
                event.speakers.filter(is_confirmed=True), many=True, context=self.context
            ).data,
        }


class VillagesListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = PublicVillageListSerializer(many=True)


class VillageDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = PublicVillageDetailSerializer()


class SpeakersResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = PublicSpeakerSerializer(many=True)


class ScheduleResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    days = serializers.SerializerMethodField()

    def get_days(self, event):
        sessions = Session.objects.filter(event=event).order_by('day_number', 'order')
        days = []
        for day in sorted(set(sessions.values_list('day_number', flat=True))):
            days.append({
                'dayNumber': day,
                'date': event.start_date.strftime('%B %d, %Y')
                    if day == 1 and event.start_date
                    else (event.end_date.strftime('%B %d, %Y') if event.end_date else ''),
                'dayLabel': f'Day {day}',
                'sessions': PublicSessionSerializer(
                    sessions.filter(day_number=day), many=True
                ).data,
            })
        return days


class RegistrationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    referenceNo = serializers.CharField(source='reference_no')
    badgeCode = serializers.CharField(source='badge_code')
    message = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    def get_message(self, obj):
        if obj.type == Registration.RegType.GUEST:
            return 'Registration confirmed. Entry badge sent to your email.'
        return None

    def get_data(self, obj):
        return {
            'id': str(obj.id), 'type': obj.type,
            'name': f'{obj.first_name} {obj.last_name}',
            'email': obj.email, 'status': obj.status,
        }


class BoothApplicationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    referenceNo = serializers.CharField(source='reference_no')
    message = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    def get_message(self, obj):
        return f'Your booth application for {obj.village.name} has been received.'

    def get_data(self, obj):
        return {
            'id': str(obj.id), 'referenceNo': obj.reference_no,
            'village': {
                'slug': obj.village.slug, 'name': obj.village.name,
                'hall': obj.village.hall,
            },
            'companyName': obj.company_name,
            'boothPackage': obj.booth_package,
            'status': obj.status, 'createdAt': obj.created_at,
        }


class AdminMetricsResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, event):
        guests = Registration.objects.filter(event=event, type=Registration.RegType.GUEST).count()
        speakers = Registration.objects.filter(event=event, type=Registration.RegType.SPEAKER).count()
        volunteers = Registration.objects.filter(event=event, type=Registration.RegType.VOLUNTEER).count()
        booths = BoothApplication.objects.filter(event=event, status=BoothApplication.Status.ALLOCATED).count()

        village_occupancy = []
        for village in event.villages.all():
            allocated = BoothApplication.objects.filter(village=village, status=BoothApplication.Status.ALLOCATED).count()
            capacity = village.booths.count() or 1
            village_occupancy.append({
                'slug': village.slug, 'name': village.name,
                'allocatedBooths': allocated, 'capacity': capacity,
                'occupancyRate': f'{(allocated / capacity) * 100:.1f}%',
            })

        return {
            'totalRegistrations': guests + speakers + volunteers + booths,
            'breakdown': {
                'guests': guests, 'booths': booths,
                'speakers': speakers, 'volunteers': volunteers,
            },
            'villageOccupancy': village_occupancy,
            'pendingBoothApplications': BoothApplication.objects.filter(
                event=event, status=BoothApplication.Status.PENDING_REVIEW
            ).count(),
        }


class BoothStatusUpdateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = BoothApplicationSerializer()


class EventActionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = ExpoEventSerializer()
