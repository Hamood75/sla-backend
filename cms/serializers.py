from rest_framework import serializers

from .models import (
    AboutSection,
    AnnouncementBar,
    BrandValue,
    ContactMessage,
    DonateModalCopy,
    Donation,
    DonationTier,
    Event,
    GalleryImage,
    GallerySection,
    HeroProgressBar,
    HeroSection,
    HeroTag,
    ImpactStat,
    MeetingRequest,
    NavItem,
    NewsletterSubscriber,
    OrgChartNode,
    PaymentMethod,
    Product,
    Program,
    Project,
    SiteSettings,
    SocialLink,
    TeamMember,
)


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = '__all__'


class AnnouncementBarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementBar
        fields = '__all__'


class NavItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavItem
        fields = '__all__'


class HeroTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroTag
        fields = ['id', 'label', 'order']


class HeroProgressBarSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroProgressBar
        fields = ['id', 'label', 'display_value', 'percent', 'color_variant', 'order']


class HeroSectionSerializer(serializers.ModelSerializer):
    tags = HeroTagSerializer(many=True, read_only=True)
    progress_bars = HeroProgressBarSerializer(many=True, read_only=True)

    class Meta:
        model = HeroSection
        fields = '__all__'


class ImpactStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactStat
        fields = '__all__'


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'


class GallerySectionSerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = GallerySection
        fields = '__all__'


class AboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = '__all__'


class BrandValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandValue
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


class OrgChartNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgChartNode
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'


class MeetingRequestSerializer(serializers.ModelSerializer):
    official_name = serializers.CharField(source='official.name', read_only=True)
    official_role = serializers.CharField(source='official.role', read_only=True)

    class Meta:
        model = MeetingRequest
        fields = [
            'id', 'official', 'official_name', 'official_role',
            'name', 'email', 'phone', 'organization',
            'preferred_at', 'topic', 'message',
            'status', 'admin_notes', 'ip_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'admin_notes', 'ip_address', 'created_at', 'updated_at']


class MeetingRequestAdminSerializer(MeetingRequestSerializer):
    class Meta(MeetingRequestSerializer.Meta):
        read_only_fields = ['ip_address', 'created_at', 'updated_at']


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    replied_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ContactMessage
        fields = [
            'id',
            'name',
            'email',
            'subject',
            'message',
            'status',
            'ip_address',
            'admin_reply',
            'replied_at',
            'replied_by',
            'replied_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'ip_address',
            'admin_reply',
            'replied_at',
            'replied_by',
            'replied_by_name',
            'created_at',
            'updated_at',
        ]

    def get_replied_by_name(self, obj):
        if not obj.replied_by:
            return ''
        return obj.replied_by.get_full_name() or obj.replied_by.username

    def create(self, validated_data):
        validated_data.pop('status', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Backoffice may only change status from the list UI
        status_value = validated_data.get('status')
        if status_value is not None:
            instance.status = status_value
            instance.save(update_fields=['status', 'updated_at'])
        return instance


class ContactMessageReplySerializer(serializers.Serializer):
    body = serializers.CharField(min_length=1)
    subject = serializers.CharField(required=False, allow_blank=True, max_length=200)


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'source', 'is_active', 'created_at']
        read_only_fields = ['is_active']


class DonationTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationTier
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class DonateModalCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonateModalCopy
        fields = '__all__'


class DonationSerializer(serializers.ModelSerializer):
    payment_method_code = serializers.SlugRelatedField(
        source='payment_method',
        slug_field='code',
        queryset=PaymentMethod.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Donation
        fields = [
            'id', 'amount', 'currency', 'donation_type', 'payment_method',
            'payment_method_code', 'phone', 'status', 'external_reference',
            'transaction_reference', 'donor_name', 'donor_email', 'created_at',
        ]
        read_only_fields = [
            'status', 'external_reference', 'transaction_reference', 'created_at', 'payment_method',
        ]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class HomepageSerializer(serializers.Serializer):
    settings = SiteSettingsSerializer()
    announcement = AnnouncementBarSerializer(allow_null=True)
    nav = NavItemSerializer(many=True)
    hero = HeroSectionSerializer(allow_null=True)
    stats = ImpactStatSerializer(many=True)
    gallery = GallerySectionSerializer(allow_null=True)
    about = AboutSectionSerializer(allow_null=True)
    values = BrandValueSerializer(many=True)
    programs = ProgramSerializer(many=True)
    org_chart = OrgChartNodeSerializer(many=True)
    team = TeamMemberSerializer(many=True)
    social_links = SocialLinkSerializer(many=True)
    donate = serializers.DictField()
