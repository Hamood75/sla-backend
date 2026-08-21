import hashlib
import hmac
import json
import time
from decimal import Decimal

from django.conf import settings
from django.db.models import Q, Count as models_Count
from django.http import FileResponse, Http404, HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsBackofficeUser

from .emailing import LOGO_PATH
from .models import (
    AboutSection,
    AnnouncementBar,
    BrandValue,
    ContactMessage,
    DonateModalCopy,
    Donation,
    DonationConfirmation,
    DonationTier,
    Event,
    GalleryImage,
    GallerySection,
    HeroSection,
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
from .serializers import (
    AboutSectionSerializer,
    AnnouncementBarSerializer,
    BrandValueSerializer,
    ContactMessageReplySerializer,
    ContactMessageSerializer,
    DonateModalCopySerializer,
    DonationConfirmationSerializer,
    DonationSerializer,
    DonationStatsSerializer,
    DonationTierSerializer,
    EventSerializer,
    GalleryImageSerializer,
    GallerySectionSerializer,
    HeroSectionSerializer,
    ImpactStatSerializer,
    MeetingRequestAdminSerializer,
    MeetingRequestSerializer,
    NavItemSerializer,
    NewsletterSubscriberSerializer,
    OrgChartNodeSerializer,
    PaymentMethodSerializer,
    ProductSerializer,
    ProgramSerializer,
    ProjectSerializer,
    SiteSettingsSerializer,
    SocialLinkSerializer,
    TeamMemberSerializer,
)


class EmailLogoView(APIView):
    """Public PNG for branded emails (hosted URL avoids Gmail attachment chips)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        if not LOGO_PATH.is_file():
            raise Http404('Email logo not found')
        response = FileResponse(LOGO_PATH.open('rb'), content_type='image/png')
        response['Cache-Control'] = 'public, max-age=86400'
        response['Content-Disposition'] = 'inline; filename="sla-email-logo.png"'
        return response


class HomepageAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings_obj = SiteSettings.load()
        announcement = AnnouncementBar.objects.filter(is_active=True).order_by('-updated_at').first()
        hero = HeroSection.objects.filter(is_active=True).prefetch_related('tags', 'progress_bars').first()
        gallery = GallerySection.objects.filter(is_active=True).prefetch_related('images').first()
        about = AboutSection.objects.filter(is_active=True).first()
        donate_copy = DonateModalCopy.load()

        payload = {
            'settings': SiteSettingsSerializer(settings_obj, context={'request': request}).data,
            'announcement': AnnouncementBarSerializer(announcement).data if announcement else None,
            'nav': NavItemSerializer(NavItem.objects.filter(is_active=True), many=True).data,
            'hero': HeroSectionSerializer(hero, context={'request': request}).data if hero else None,
            'stats': ImpactStatSerializer(ImpactStat.objects.filter(is_active=True), many=True).data,
            'gallery': GallerySectionSerializer(gallery, context={'request': request}).data if gallery else None,
            'about': AboutSectionSerializer(about).data if about else None,
            'values': BrandValueSerializer(BrandValue.objects.filter(is_active=True), many=True).data,
            'programs': ProgramSerializer(Program.objects.filter(is_active=True), many=True).data,
            'org_chart': OrgChartNodeSerializer(OrgChartNode.objects.filter(is_active=True), many=True).data,
            'team': TeamMemberSerializer(
                TeamMember.objects.filter(is_published=True),
                many=True,
                context={'request': request},
            ).data,
            'social_links': SocialLinkSerializer(SocialLink.objects.filter(is_active=True), many=True).data,
            'donate': {
                'copy': DonateModalCopySerializer(donate_copy).data,
                'tiers': DonationTierSerializer(DonationTier.objects.filter(is_active=True), many=True).data,
                'payment_methods': PaymentMethodSerializer(
                    PaymentMethod.objects.filter(is_active=True),
                    many=True,
                ).data,
            },
        }
        return Response(payload)


class SiteSettingsView(APIView):
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get(self, request):
        return Response(SiteSettingsSerializer(SiteSettings.load(), context={'request': request}).data)

    def put(self, request):
        obj = SiteSettings.load()
        serializer = SiteSettingsSerializer(obj, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        return self.put(request)


class BackofficeModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsBackofficeUser]


class AnnouncementBarViewSet(BackofficeModelViewSet):
    queryset = AnnouncementBar.objects.all()
    serializer_class = AnnouncementBarSerializer


class NavItemViewSet(BackofficeModelViewSet):
    queryset = NavItem.objects.all()
    serializer_class = NavItemSerializer


class HeroSectionViewSet(BackofficeModelViewSet):
    queryset = HeroSection.objects.prefetch_related('tags', 'progress_bars')
    serializer_class = HeroSectionSerializer


class ImpactStatViewSet(BackofficeModelViewSet):
    queryset = ImpactStat.objects.all()
    serializer_class = ImpactStatSerializer
    filterset_fields = ['placement', 'is_active']


class GallerySectionViewSet(BackofficeModelViewSet):
    queryset = GallerySection.objects.prefetch_related('images')
    serializer_class = GallerySectionSerializer


class GalleryImageViewSet(BackofficeModelViewSet):
    queryset = GalleryImage.objects.select_related('section')
    serializer_class = GalleryImageSerializer


class AboutSectionViewSet(BackofficeModelViewSet):
    queryset = AboutSection.objects.all()
    serializer_class = AboutSectionSerializer


class BrandValueViewSet(BackofficeModelViewSet):
    queryset = BrandValue.objects.all()
    serializer_class = BrandValueSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    lookup_field = 'pk'
    search_fields = ['title', 'tag']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve') and not getattr(self.request.user, 'is_backoffice_user', False):
            return qs.filter(is_active=True)
        return qs


class OrgChartNodeViewSet(BackofficeModelViewSet):
    queryset = OrgChartNode.objects.all()
    serializer_class = OrgChartNodeSerializer


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.select_related('org_role')
    serializer_class = TeamMemberSerializer
    search_fields = ['name', 'role']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve') and not getattr(self.request.user, 'is_backoffice_user', False):
            return qs.filter(is_published=True)
        return qs


class MeetingRequestViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = MeetingRequest.objects.select_related('official')
    filterset_fields = ['status', 'official']
    search_fields = ['name', 'email', 'topic', 'official__name']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get_serializer_class(self):
        if self.action == 'create':
            return MeetingRequestSerializer
        return MeetingRequestAdminSerializer

    def perform_create(self, serializer):
        official = serializer.validated_data['official']
        if not official.is_published or not official.accepts_meetings:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'official': 'This official is not available for meetings.'})
        ip = self.request.META.get('REMOTE_ADDR')
        meeting = serializer.save(ip_address=ip, status=MeetingRequest.Status.PENDING)
        from .emailing import notify_meeting_request
        notify_meeting_request(meeting)


class SocialLinkViewSet(BackofficeModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer


class ContactMessageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ContactMessage.objects.select_related('replied_by').all()
    serializer_class = ContactMessageSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'email', 'subject', 'message']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def perform_create(self, serializer):
        ip = self.request.META.get('REMOTE_ADDR')
        msg = serializer.save(ip_address=ip)
        from .emailing import notify_contact_received
        notify_contact_received(msg)

    def perform_update(self, serializer):
        # Public cannot update; backoffice may mark read / update status only
        serializer.save()

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        msg = self.get_object()
        serializer = ContactMessageReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body = serializer.validated_data['body'].strip()
        subject_override = (serializer.validated_data.get('subject') or '').strip()

        original_subject = msg.subject.strip() if msg.subject else 'your message'
        subject = subject_override or f'Re: {original_subject}'

        from .emailing import send_contact_reply

        if not send_contact_reply(msg=msg, body=body, subject=subject):
            return Response(
                {'detail': 'Could not send email. Check SMTP settings and try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        msg.status = ContactMessage.Status.REPLIED
        msg.admin_reply = body
        msg.replied_at = timezone.now()
        if request.user and request.user.is_authenticated:
            msg.replied_by = request.user
        msg.save(update_fields=['status', 'admin_reply', 'replied_at', 'replied_by', 'updated_at'])
        return Response(ContactMessageSerializer(msg).data)


class NewsletterSubscriberViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]


class DonationTierViewSet(BackofficeModelViewSet):
    queryset = DonationTier.objects.all()
    serializer_class = DonationTierSerializer


class PaymentMethodViewSet(BackofficeModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class DonateModalCopyView(APIView):
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get(self, request):
        return Response(DonateModalCopySerializer(DonateModalCopy.load()).data)

    def put(self, request):
        obj = DonateModalCopy.load()
        serializer = DonateModalCopySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DonationViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Donation.objects.select_related('payment_method')
    serializer_class = DonationSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['status', 'confirmed', 'currency', 'donation_type']
    search_fields = ['donor_name', 'donor_email', 'transaction_reference', 'payment_id']
    ordering_fields = ['created_at', 'amount']


class DonationConfirmationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DonationConfirmation.objects.select_related('donation')
    serializer_class = DonationConfirmationSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event_type', 'duplicate', 'processed', 'donation']
    search_fields = ['event_id']
    ordering_fields = ['created_at', 'received_at']


class DonationWebhookView(APIView):
    """Receive Pay-IT webhook events, verify signature, confirm/create donations."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        secret = settings.PAYIT_SECRET_KEY
        if not secret:
            return HttpResponse('Webhook secret not configured', status=500)

        signature = request.headers.get('PayIT-Signature', '')
        timestamp = request.headers.get('PayIT-Timestamp', '')
        header_event_id = request.headers.get('PayIT-Event-Id', '')

        if not signature or not timestamp or not header_event_id:
            return HttpResponse('Missing required Pay-IT headers', status=400)

        # Replay tolerance check
        try:
            ts_int = int(timestamp)
        except (ValueError, TypeError):
            return HttpResponse('Invalid timestamp', status=400)

        tolerance = settings.PAYIT_WEBHOOK_TOLERANCE_SECONDS
        if abs(time.time() - ts_int) > tolerance:
            return HttpResponse('Timestamp outside tolerance window', status=401)

        # Read raw body for signature verification
        raw_body = request.body
        if not raw_body:
            return HttpResponse('Empty body', status=400)

        # Compute expected signature: v1=HMAC-SHA256(secret, timestamp + "." + raw_body)
        signed_payload = f'{timestamp}.'.encode() + raw_body
        expected_sig = 'v1=' + hmac.new(
            secret.encode(), signed_payload, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return HttpResponse('Invalid signature', status=401)

        # Parse the verified body
        try:
            event = json.loads(raw_body)
        except (json.JSONDecodeError, ValueError):
            return HttpResponse('Invalid JSON', status=400)

        # Confirm header event ID matches body id
        body_event_id = event.get('id', '')
        if body_event_id != header_event_id:
            return HttpResponse('Event ID mismatch', status=400)

        result = self._process_event(event)
        return Response({'processed': 1, 'results': [result]}, status=status.HTTP_200_OK)

    def _process_event(self, event):
        event_id = event.get('id', '')
        event_type = event.get('type', '')
        created_at = event.get('created_at', '')
        data = event.get('data', {}) or {}

        if not event_id:
            return {'error': 'event id is required', 'processed': False}

        confirmation, created = DonationConfirmation.objects.get_or_create(
            event_id=str(event_id),
            defaults={
                'event_type': str(event_type),
                'received_at': parse_datetime(created_at) if created_at else None,
                'timestamp': str(event.get('api_version', '')),
                'duplicate': False,
                'payload': event,
            },
        )

        if not created:
            return {'event_id': str(event_id), 'status': 'already recorded', 'processed': False}

        payment_id = data.get('payment_id', '')
        payment_link_id = data.get('payment_link_id', '')
        amount = data.get('amount')
        currency = data.get('currency', 'TZS')
        channel = data.get('initiation_channel', '')
        status_value = data.get('status', '')
        donor_name = data.get('donor_name', '') or data.get('customer_name', '')
        donor_email = data.get('donor_email', '') or data.get('customer_email', '')
        new_status = Donation.Status.PENDING
        confirmed = False
        if event_type.endswith('.succeeded') or status_value == 'succeeded':
            new_status = Donation.Status.SUCCESS
            confirmed = True
        elif event_type.endswith('.failed') or status_value == 'failed':
            new_status = Donation.Status.FAILED
        elif event_type.endswith('.expired') or status_value == 'expired':
            new_status = Donation.Status.FAILED

        defaults = {
            'amount': Decimal(amount) if amount is not None else Decimal('0.00'),
            'currency': currency,
            'payment_link_id': payment_link_id,
            'initiation_channel': channel,
            'status': new_status,
            'confirmed': confirmed,
            'raw_gateway_response': event,
        }
        defaults['donor_name'] = donor_name if donor_name else 'Anonymous'
        if donor_email:
            defaults['donor_email'] = donor_email

        if payment_id:
            defaults['payment_id'] = payment_id
            defaults['external_reference'] = payment_id

        donation = None
        if payment_id:
            donation = Donation.objects.filter(payment_id=payment_id).first()

        if donation:
            for key, value in defaults.items():
                setattr(donation, key, value)
            donation.save(update_fields=list(defaults.keys()) + ['updated_at'])
        else:
            if payment_id:
                defaults['transaction_reference'] = payment_id
            donation = Donation.objects.create(**defaults)

        confirmation.donation = donation
        confirmation.processed = True
        confirmation.save(update_fields=['donation', 'processed'])

        return {
            'event_id': str(event_id),
            'donation_id': donation.pk,
            'status': donation.status,
            'confirmed': donation.confirmed,
        }


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'slug'
    search_fields = ['title', 'slug']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve') and not getattr(self.request.user, 'is_backoffice_user', False):
            return qs.filter(is_published=True)
        return qs


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'slug'
    search_fields = ['title', 'slug', 'location']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve') and not getattr(self.request.user, 'is_backoffice_user', False):
            return qs.filter(is_published=True)
        return qs


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    search_fields = ['title', 'slug']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve') and not getattr(self.request.user, 'is_backoffice_user', False):
            return qs.filter(is_published=True)
        return qs


class DonationStatsAPIView(APIView):
    permission_classes = [IsBackofficeUser]

    def get(self, request):
        from django.db.models import Sum

        qs = Donation.objects.all()
        confirmed_qs = qs.filter(confirmed=True)

        data = {
            'total_donations': qs.count(),
            'successful': qs.filter(status=Donation.Status.SUCCESS).count(),
            'pending': qs.filter(status=Donation.Status.PENDING).count(),
            'failed': qs.filter(status=Donation.Status.FAILED).count(),
            'confirmed_total': confirmed_qs.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00'),
            'confirmed_count': confirmed_qs.count(),
            'confirmed_by_currency': list(
                confirmed_qs.values('currency').annotate(
                    total=Sum('amount'),
                    count=models_Count('id'),
                ).order_by('-total')
            ),
        }
        serializer = DonationStatsSerializer(data)
        return Response(serializer.data)


class DashboardStatsAPIView(APIView):
    permission_classes = [IsBackofficeUser]

    def get(self, request):
        from profiles.models import EmployeeProfile
        from qr.models import QRCode, QRCodeAnalytics

        return Response({
            'qr_codes': QRCode.objects.count(),
            'active_qr_codes': QRCode.objects.filter(is_active=True).count(),
            'total_scans': QRCodeAnalytics.objects.count(),
            'profiles': EmployeeProfile.objects.filter(is_public=True).count(),
            'team_members': TeamMember.objects.filter(is_published=True).count(),
            'programs': Program.objects.filter(is_active=True).count(),
            'projects': Project.objects.filter(is_published=True).count(),
            'events': Event.objects.filter(is_published=True).count(),
            'contact_messages_new': ContactMessage.objects.filter(status=ContactMessage.Status.NEW).count(),
            'meeting_requests_pending': MeetingRequest.objects.filter(
                status=MeetingRequest.Status.PENDING
            ).count(),
            'newsletter_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
            'donations': Donation.objects.filter(status=Donation.Status.SUCCESS).count(),
        })
