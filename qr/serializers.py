from rest_framework import serializers

from .models import QRCode, QRCodeAnalytics, QRCodeLink


class QRCodeLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(max_length=500)

    class Meta:
        model = QRCodeLink
        fields = ['id', 'label', 'icon', 'url', 'order', 'is_active', 'click_count']
        read_only_fields = ['click_count']


class QRCodeSerializer(serializers.ModelSerializer):
    links = QRCodeLinkSerializer(many=True, required=False)
    public_url = serializers.CharField(read_only=True)
    public_path = serializers.CharField(read_only=True)
    owner_name = serializers.SerializerMethodField()
    is_currently_active = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            'id', 'code', 'slug', 'owner', 'owner_name', 'title', 'description',
            'destination_type', 'destination_url', 'content_type', 'object_id',
            'theme', 'primary_color', 'secondary_color', 'background_color',
            'logo', 'show_logo', 'is_active', 'password', 'expires_at', 'activates_at',
            'scan_count', 'links', 'public_url', 'public_path', 'is_currently_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['owner', 'scan_count', 'code']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'allow_blank': True},
        }

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_is_currently_active(self, obj):
        return obj.is_currently_active()

    def create(self, validated_data):
        links_data = validated_data.pop('links', [])
        qr = QRCode.objects.create(**validated_data)
        for link in links_data:
            QRCodeLink.objects.create(qr=qr, **link)
        return qr

    def update(self, instance, validated_data):
        links_data = validated_data.pop('links', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if links_data is not None:
            instance.links.all().delete()
            for link in links_data:
                QRCodeLink.objects.create(qr=instance, **link)
        return instance


class QRCodeAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeAnalytics
        fields = [
            'id', 'qr', 'country', 'city', 'device', 'browser', 'os',
            'referrer', 'latitude', 'longitude', 'is_returning',
            'link_clicked', 'timestamp',
        ]


class QRHubSerializer(serializers.ModelSerializer):
    links = QRCodeLinkSerializer(many=True, read_only=True)
    destination = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            'code', 'title', 'description', 'destination_type', 'theme',
            'primary_color', 'secondary_color', 'background_color',
            'logo', 'show_logo', 'links', 'destination',
        ]

    def get_destination(self, obj):
        return obj.resolve_destination()
