from rest_framework import serializers

from .models import EmployeeProfile, ProfileProject, ProfileSocialLink


class ProfileSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSocialLink
        fields = ['id', 'platform', 'label', 'url', 'icon', 'order', 'is_active']


class ProfileProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='project.title', read_only=True)
    slug = serializers.CharField(source='project.slug', read_only=True)
    summary = serializers.CharField(source='project.summary', read_only=True)

    class Meta:
        model = ProfileProject
        fields = ['id', 'project', 'title', 'slug', 'summary', 'order']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    social_links = ProfileSocialLinkSerializer(many=True, required=False)
    featured_projects = ProfileProjectSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'username', 'display_name', 'position', 'bio', 'photo',
            'email', 'phone', 'website', 'location', 'meeting_url', 'vcard_enabled',
            'theme_primary', 'theme_secondary', 'is_public', 'department',
            'department_name', 'social_links', 'featured_projects',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        social_data = validated_data.pop('social_links', [])
        profile = EmployeeProfile.objects.create(**validated_data)
        for item in social_data:
            ProfileSocialLink.objects.create(profile=profile, **item)
        return profile

    def update(self, instance, validated_data):
        social_data = validated_data.pop('social_links', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if social_data is not None:
            instance.social_links.all().delete()
            for item in social_data:
                ProfileSocialLink.objects.create(profile=instance, **item)
        return instance
