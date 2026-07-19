from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsBackofficeUser, IsOwnerOrBackoffice

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
