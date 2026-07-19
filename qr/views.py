from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsBackofficeUser, IsOwnerOrBackoffice

from .models import QRCode, QRCodeAnalytics, QRCodeLink
from .serializers import QRCodeAnalyticsSerializer, QRCodeSerializer, QRHubSerializer
from .services import build_qr_image, record_scan


class QRCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QRCodeSerializer
    lookup_field = 'code'
    search_fields = ['code', 'title', 'slug']
    filterset_fields = ['destination_type', 'is_active', 'theme']

    def get_queryset(self):
        qs = QRCode.objects.select_related('owner').prefetch_related('links')
        user = self.request.user
        if user.is_authenticated and getattr(user, 'is_backoffice_user', False):
            return qs
        if user.is_authenticated:
            return qs.filter(owner=user)
        return qs.none()

    def get_permissions(self):
        if self.action in ('resolve', 'hub', 'track_link'):
            return [permissions.AllowAny()]
        if self.action in ('list', 'create', 'bulk'):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrBackoffice()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='image')
    def image(self, request, code=None):
        qr = self.get_object()
        fmt = request.query_params.get('export', request.query_params.get('fmt', 'png')).lower()
        if fmt not in ('png', 'svg'):
            return Response({'detail': 'export must be png or svg'}, status=400)
        data, content_type = build_qr_image(qr, fmt=fmt)
        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{qr.code}.{fmt}"'
        return response

    @action(detail=True, methods=['get'], url_path='analytics')
    def analytics(self, request, code=None):
        qr = self.get_object()
        scans = qr.scans.all()
        daily = (
            scans.annotate(day=TruncDate('timestamp'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        monthly = (
            scans.annotate(month=TruncMonth('timestamp'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        by_device = scans.values('device').annotate(count=Count('id')).order_by('-count')
        by_browser = scans.values('browser').annotate(count=Count('id')).order_by('-count')
        by_country = scans.values('country').annotate(count=Count('id')).order_by('-count')
        by_city = scans.values('city').annotate(count=Count('id')).order_by('-count')
        popular_links = (
            qr.links.annotate(clicks=Count('analytics'))
            .values('id', 'label', 'url', 'click_count', 'clicks')
            .order_by('-click_count')
        )
        returning = scans.filter(is_returning=True).count()
        return Response({
            'total_scans': qr.scan_count,
            'returning_users': returning,
            'daily': list(daily),
            'monthly': list(monthly),
            'devices': list(by_device),
            'browsers': list(by_browser),
            'countries': list(by_country),
            'cities': list(by_city),
            'popular_links': list(popular_links),
            'recent': QRCodeAnalyticsSerializer(scans[:50], many=True).data,
        })

    @action(detail=False, methods=['get'], url_path=r'resolve/(?P<code>[^/.]+)')
    def resolve(self, request, code=None):
        try:
            qr = QRCode.objects.prefetch_related('links').get(code__iexact=code)
        except QRCode.DoesNotExist:
            return Response({'detail': 'QR code not found'}, status=404)

        password = request.query_params.get('password', '')
        if qr.password and qr.password != password:
            return Response({'detail': 'Password required', 'requires_password': True}, status=403)

        if not qr.is_currently_active():
            return Response({'detail': 'QR code is inactive or expired'}, status=410)

        record_scan(qr, request)

        if qr.destination_type == QRCode.DestinationType.HUB or qr.links.filter(is_active=True).exists():
            return Response({
                'mode': 'hub',
                'hub': QRHubSerializer(qr, context={'request': request}).data,
            })

        destination = qr.resolve_destination()
        return Response({
            'mode': 'redirect',
            'destination': destination,
            'hub': QRHubSerializer(qr, context={'request': request}).data,
        })

    @action(detail=False, methods=['get'], url_path=r'hub/(?P<code>[^/.]+)')
    def hub(self, request, code=None):
        try:
            qr = QRCode.objects.prefetch_related('links').get(code__iexact=code)
        except QRCode.DoesNotExist:
            return Response({'detail': 'QR code not found'}, status=404)
        if not qr.is_currently_active():
            return Response({'detail': 'QR code is inactive or expired'}, status=410)
        record_scan(qr, request)
        return Response(QRHubSerializer(qr, context={'request': request}).data)

    @action(detail=False, methods=['post'], url_path=r'track-link/(?P<code>[^/.]+)/(?P<link_id>[0-9]+)')
    def track_link(self, request, code=None, link_id=None):
        try:
            qr = QRCode.objects.get(code__iexact=code)
            link = qr.links.get(pk=link_id, is_active=True)
        except (QRCode.DoesNotExist, QRCodeLink.DoesNotExist):
            return Response({'detail': 'Not found'}, status=404)
        link.click_count += 1
        link.save(update_fields=['click_count'])
        record_scan(qr, request, link_clicked=link)
        return Response({'url': link.url, 'click_count': link.click_count})

    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk(self, request):
        items = request.data.get('items', [])
        if not isinstance(items, list) or not items:
            return Response({'detail': 'items array required'}, status=400)
        created = []
        for item in items[:100]:
            serializer = QRCodeSerializer(data=item, context={'request': request})
            serializer.is_valid(raise_exception=True)
            created.append(serializer.save(owner=request.user))
        return Response(
            QRCodeSerializer(created, many=True, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class PlatformAnalyticsAPIView(APIView):
    permission_classes = [IsBackofficeUser]

    def get(self, request):
        scans = QRCodeAnalytics.objects.all()
        daily = (
            scans.annotate(day=TruncDate('timestamp'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('-day')[:30]
        )
        by_country = scans.values('country').annotate(count=Count('id')).order_by('-count')[:20]
        top_qr = (
            QRCode.objects.annotate(scans_total=Count('scans'))
            .order_by('-scans_total')[:10]
            .values('code', 'title', 'scans_total', 'scan_count')
        )
        return Response({
            'total_scans': scans.count(),
            'total_qr_codes': QRCode.objects.count(),
            'daily': list(daily),
            'countries': list(by_country),
            'top_qr_codes': list(top_qr),
        })
