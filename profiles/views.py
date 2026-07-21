import re

from django.conf import settings
from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsBackofficeUser, IsOwnerOrBackoffice
from qr.models import QRCode, QRCodeLink

from .models import EmployeeProfile
from .serializers import EmployeeProfileSerializer


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.select_related('user', 'department').prefetch_related(
        'social_links', 'featured_projects__project',
    )
    serializer_class = EmployeeProfileSerializer
    lookup_field = 'username'
    search_fields = ['username', 'display_name', 'position', 'email']
    filterset_fields = ['is_public', 'department']

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'vcard'):
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrBackoffice()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if self.action in ('list', 'retrieve', 'vcard'):
            if user.is_authenticated and getattr(user, 'is_backoffice_user', False):
                return qs
            return qs.filter(is_public=True)
        if user.is_authenticated and getattr(user, 'is_backoffice_user', False):
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _absolute_profile_url(self, profile):
        base = getattr(settings, 'PUBLIC_SITE_URL', 'https://streetlabsafrica.org').rstrip('/')
        return f'{base}/profiles/{profile.username}'

    def _absolute_vcard_url(self, profile):
        base = getattr(settings, 'PUBLIC_SITE_URL', 'https://streetlabsafrica.org').rstrip('/')
        return f'{base}/api/profiles/{profile.username}/vcard/'

    def _profile_qr_slug(self, profile):
        return f'profile-{profile.pk}'

    def _qr_icon_for_platform(self, platform):
        valid_icons = {choice[0] for choice in QRCodeLink.Icon.choices}
        return platform if platform in valid_icons else QRCodeLink.Icon.CUSTOM

    def _build_profile_qr_links(self, profile):
        links = []

        if profile.website:
            links.append({
                'label': 'Website',
                'icon': QRCodeLink.Icon.WEBSITE,
                'url': profile.website,
            })

        links.append({
            'label': 'Employee Profile',
            'icon': QRCodeLink.Icon.PROFILE,
            'url': self._absolute_profile_url(profile),
        })

        if profile.email:
            links.append({
                'label': 'Email',
                'icon': QRCodeLink.Icon.EMAIL,
                'url': f'mailto:{profile.email}',
            })

        phone_digits = re.sub(r'\D+', '', profile.phone or '')
        if phone_digits:
            links.append({
                'label': 'WhatsApp',
                'icon': QRCodeLink.Icon.WHATSAPP,
                'url': f'https://wa.me/{phone_digits}',
            })

        if profile.vcard_enabled:
            links.append({
                'label': 'Download Contact',
                'icon': QRCodeLink.Icon.CONTACT,
                'url': self._absolute_vcard_url(profile),
            })

        for social in profile.social_links.filter(is_active=True):
            if not social.url:
                continue
            links.append({
                'label': social.label or social.get_platform_display(),
                'icon': self._qr_icon_for_platform(social.platform),
                'url': social.url,
            })

        return [
            {
                **link,
                'order': index,
                'is_active': True,
            }
            for index, link in enumerate(links, start=1)
        ]

    @action(detail=True, methods=['get'], url_path='vcard')
    def vcard(self, request, username=None):
        profile = self.get_object()
        if not profile.vcard_enabled:
            return Response({'detail': 'vCard disabled'}, status=status.HTTP_404_NOT_FOUND)

        lines = [
            'BEGIN:VCARD',
            'VERSION:3.0',
            f'FN:{profile.display_name}',
            f'TITLE:{profile.position}',
            f'ORG:Street Labs Africa',
        ]
        if profile.email:
            lines.append(f'EMAIL;TYPE=INTERNET:{profile.email}')
        if profile.phone:
            lines.append(f'TEL;TYPE=CELL:{profile.phone}')
        if profile.website:
            lines.append(f'URL:{profile.website}')
        if profile.location:
            lines.append(f'ADR;TYPE=WORK:;;{profile.location};;;;')
        lines.append('END:VCARD')
        content = '\r\n'.join(lines) + '\r\n'
        response = HttpResponse(content, content_type='text/vcard')
        response['Content-Disposition'] = f'attachment; filename="{profile.username}.vcf"'
        return response

    @action(detail=True, methods=['post'], url_path='ensure-qr')
    def ensure_qr(self, request, username=None):
        profile = self.get_object()
        qr = QRCode.objects.filter(slug=self._profile_qr_slug(profile)).first()

        if qr is None:
            qr = QRCode.objects.create(
                owner=profile.user,
                slug=self._profile_qr_slug(profile),
                title=f'{profile.display_name} Smart Hub',
                description=profile.position or '',
                destination_type=QRCode.DestinationType.HUB,
                primary_color=getattr(profile, 'theme_primary', '#ff6a00') or '#ff6a00',
                secondary_color=getattr(profile, 'theme_secondary', '#0a1f44') or '#0a1f44',
                background_color='#ffffff',
                is_active=True,
            )
        else:
            qr.owner = profile.user
            qr.title = f'{profile.display_name} Smart Hub'
            qr.description = profile.position or ''
            qr.destination_type = QRCode.DestinationType.HUB
            qr.primary_color = getattr(profile, 'theme_primary', '#ff6a00') or '#ff6a00'
            qr.secondary_color = getattr(profile, 'theme_secondary', '#0a1f44') or '#0a1f44'
            qr.background_color = '#ffffff'
            qr.is_active = True
            qr.save()

        qr.links.all().delete()
        for link in self._build_profile_qr_links(profile):
            QRCodeLink.objects.create(qr=qr, **link)

        return Response({
            'code': qr.code,
            'title': qr.title,
            'public_url': qr.public_url,
            'public_path': qr.public_path,
            'link_count': qr.links.count(),
        })
