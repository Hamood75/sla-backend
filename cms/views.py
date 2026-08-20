from decimal import Decimal

from django.db.models import Q
from django.http import FileResponse, Http404
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
    """Receive payment gateway webhook events and confirm/create donations."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        events = request.data
        if not isinstance(events, list):
            events = [events]

        results = []
        for event in events:
            results.append(self._process_event(event))

        return Response({'processed': len(results), 'results': results}, status=status.HTTP_200_OK)

    def _process_event(self, event):
        payload = event.get('payload', {}) or {}
        event_id = event.get('eventId') or payload.get('id')
        event_type = event.get('eventType') or payload.get('type', '')

        if not event_id:
            return {'error': 'eventId is required', 'processed': False}

        confirmation, created = DonationConfirmation.objects.get_or_create(
            event_id=str(event_id),
            defaults={
                'event_type': str(event_type),
                'received_at': parse_datetime(event.get('receivedAt')) if event.get('receivedAt') else None,
                'timestamp': str(event.get('timestamp', '')),
                'duplicate': bool(event.get('duplicate', False)),
                'payload': event,
            },
        )

        if not created:
            return {'event_id': str(event_id), 'status': 'already recorded', 'processed': False}

        data = (payload.get('data') or {})
        payment_id = data.get('payment_id', '')
        payment_link_id = data.get('payment_link_id', '')
        amount = data.get('amount')
        currency = data.get('currency', 'TZS')
        channel = data.get('initiation_channel', '')
        status_value = data.get('status', '')
        donor = data.get('slug', '')

        new_status = Donation.Status.PENDING
        confirmed = False
        if event_type.endswith('.success') or status_value == 'success':
            new_status = Donation.Status.SUCCESS
            confirmed = True
        elif event_type.endswith('.failed') or status_value == 'failed':
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
        if donor:
            defaults['donor_name'] = donor

        if payment_id:
            defaults['payment_id'] = payment_id
            defaults['external_reference'] = payment_id

        donation = None
        if payment_id:
            donation = Donation.objects.filter(
                Q(payment_id=payment_id) | Q(external_reference=payment_id) | Q(transaction_reference=payment_id)
            ).first()
        if not donation and payment_link_id:
            donation = Donation.objects.filter(payment_link_id=payment_link_id).first()

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
