from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsBackofficeUser

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

        org = SiteSettings.load()
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@streetlabsafrica.org'
        org_name = org.org_name or 'Street Digital Labs Africa'
        org_inbox = org.email or 'info@streetlabsafrica.org'
        original_subject = msg.subject.strip() if msg.subject else 'your message'
        subject = subject_override or f'Re: {original_subject}'

        email_body = (
            f'Hi {msg.name},\n\n'
            f'{body}\n\n'
            f'—\n'
            f'{org_name}\n'
            f'{org_inbox}\n\n'
            f'---\n'
            f'On your message:\n'
            f'{msg.message}\n'
        )

        try:
            mail = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=f'{org_name} <{from_email}>',
                to=[msg.email],
                reply_to=[org_inbox],
            )
            mail.send(fail_silently=False)
        except Exception as exc:
            return Response(
                {'detail': f'Could not send email: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        msg.admin_reply = body
        msg.replied_at = timezone.now()
        msg.replied_by = request.user if request.user.is_authenticated else None
        msg.status = ContactMessage.Status.REPLIED
        msg.save(update_fields=[
            'admin_reply', 'replied_at', 'replied_by', 'status', 'updated_at',
        ])
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


class DonationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Donation.objects.select_related('payment_method')
    serializer_class = DonationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsBackofficeUser()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ref = f"SLA-{int(timezone.now().timestamp())}"
        donation = serializer.save(
            status=Donation.Status.SUCCESS,
            transaction_reference=ref,
            external_reference=ref,
        )
        return Response(DonationSerializer(donation).data, status=status.HTTP_201_CREATED)


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
