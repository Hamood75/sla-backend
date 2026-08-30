import base64
import csv
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsBackofficeUser
from django.db.models import Q
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
from .serializers import (
    AdminEventDetailSerializer,
    AdminEventEditionSerializer,
    AdminEventStatSerializer,
    AdminFocusAreaSerializer,
    AdminMetricsResponseSerializer,
    AdminPartnerSerializer,
    BoothApplicationResponseSerializer,
    BoothApplicationSerializer,
    BoothApplicationStatusUpdateSerializer,
    BoothPublicRegistrationSerializer,
    BoothStatusUpdateResponseSerializer,
    EventActionResponseSerializer,
    EventEditionSerializer,
    ExpoEventSerializer,
    HeroImageSerializer,
    ExpoVillageDetailSerializer,
    ExpoVillageListSerializer,
    GuestRegistrationSerializer,
    LandingPageResponseSerializer,
    MediaAssetSerializer,
    RegistrationResponseSerializer,
    RegistrationSerializer,
    ScheduleResponseSerializer,
    SessionSerializer,
    SpeakerRegistrationSerializer,
    SpeakerSerializer,
    SpeakersResponseSerializer,
    VillageBoothSerializer,
    VillageDetailResponseSerializer,
    VillageGallerySerializer,
    VillageHighlightSerializer,
    VillageScheduleSerializer,
    VillagesListResponseSerializer,
    VolunteerRegistrationSerializer,
)


# --- Admin ViewSets ---

class ExpoEventViewSet(viewsets.ModelViewSet):
    queryset = ExpoEvent.objects.all()
    serializer_class = ExpoEventSerializer
    permission_classes = [IsBackofficeUser]
    lookup_field = 'year'

    def get_queryset(self):
        return ExpoEvent.objects.prefetch_related(
            'stats', 'focus_areas', 'partners',
            'villages', 'speakers', 'sessions',
            'booth_applications', 'registrations', 'hero_images',
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AdminEventDetailSerializer
        return ExpoEventSerializer

    @action(detail=False, methods=['get'])
    def years(self, request):
        """List all event years/editions with status flags."""
        events = ExpoEvent.objects.all().order_by('-year')
        data = []
        for e in events:
            data.append({
                'id': str(e.id),
                'year': e.year,
                'title': e.title,
                'start_date': e.start_date,
                'end_date': e.end_date,
                'is_active': e.is_active,
                'is_published': e.is_published,
                'is_current': e.is_active,
            })
        return Response(data)

    @action(detail=True, methods=['post'], url_path='hero-images')
    def hero_images(self, request, year=None):
        """Add a hero image to the event. Accepts base64 data URI or multipart file upload."""
        event = self.get_object()
        file = request.FILES.get('file')
        b64 = request.data.get('image_base64') or request.data.get('image')
        if file:
            name = f'hero_{uuid.uuid4().hex[:8]}_{file.name}'
            image = ContentFile(file.read(), name=name)
        elif b64 and b64.startswith('data:'):
            header, _, b64_content = b64.partition(',')
            mime_type = header.split(';')[0].split(':')[1] if ':' in header else 'image/png'
            ext = mime_type.split('/')[-1].split('+')[0]
            name = f'hero_{uuid.uuid4().hex[:8]}.{ext}'
            decoded = base64.b64decode(b64_content)
            image = ContentFile(decoded, name=name)
        else:
            return Response(
                {'error': 'Provide a file via multipart or an image_base64 data URI.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order = ExpoEventHeroImage.objects.filter(event=event).count()
        hero = ExpoEventHeroImage.objects.create(event=event, image=image, order=order)
        data = HeroImageSerializer(hero, context={'request': request}).data
        return Response(
            {'message': 'Hero image added.', 'hero_image': data},
            status=status.HTTP_201_CREATED,
        )

    @hero_images.mapping.delete
    def remove_hero_image(self, request, year=None):
        """Remove one or more hero images from the event by id, path, or URL."""
        event = self.get_object()
        ids = request.data.get('ids') or request.data.get('id')
        paths = request.data.get('paths') or request.data.get('urls') or request.data.get('images')
        single = request.data.get('path') or request.data.get('url')
        if single:
            paths = [single]
        if ids:
            if not isinstance(ids, list):
                ids = [ids]
            qs = ExpoEventHeroImage.objects.filter(event=event, id__in=ids)
        elif paths and isinstance(paths, list):
            normalized = []
            for raw in paths:
                path = raw
                if 'media/' in path:
                    path = path.split('media/')[-1]
                normalized.append(path)
            qs = ExpoEventHeroImage.objects.filter(event=event, image__in=normalized)
        else:
            return Response(
                {'error': 'Provide id, ids, path, url, paths, urls, or images (list) of hero image(s) to remove.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        removed = []
        for h in qs:
            h.image.delete(save=False)
            h.delete()
            removed.append(str(h.id))
        hero_images = ExpoEventHeroImage.objects.filter(event=event).order_by('order')
        return Response({
            'message': f'Removed {len(removed)} hero image(s).',
            'removed': removed,
            'hero_images': HeroImageSerializer(hero_images, many=True, context={'request': request}).data,
        })

    @action(detail=True, methods=['patch'])
    def activate(self, request, year=None):
        event = self.get_object()
        ExpoEvent.objects.exclude(pk=event.pk).update(is_active=False)
        event.is_active = True
        event.save(update_fields=['is_active', 'updated_at'])
        return Response(EventActionResponseSerializer({
            'message': f'Event {event.year} activated.',
            'data': event,
        }).data)

    @action(detail=True, methods=['patch'])
    def publish(self, request, year=None):
        event = self.get_object()
        event.is_published = True
        event.save(update_fields=['is_published', 'updated_at'])
        return Response(EventActionResponseSerializer({
            'message': f'Event {event.year} published.',
            'data': event,
        }).data)

    @action(detail=True, methods=['patch'])
    def unpublish(self, request, year=None):
        event = self.get_object()
        event.is_published = False
        event.save(update_fields=['is_published', 'updated_at'])
        return Response(EventActionResponseSerializer({
            'message': f'Event {event.year} unpublished.',
            'data': event,
        }).data)


class EventStatViewSet(viewsets.ModelViewSet):
    queryset = EventStat.objects.all()
    serializer_class = AdminEventStatSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event']


class FocusAreaViewSet(viewsets.ModelViewSet):
    queryset = FocusArea.objects.all()
    serializer_class = AdminFocusAreaSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event']


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = AdminPartnerSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event', 'tier']


class ExpoVillageViewSet(viewsets.ModelViewSet):
    queryset = ExpoVillage.objects.all()
    serializer_class = ExpoVillageListSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event']
    lookup_field = 'slug'

    def get_queryset(self):
        return ExpoVillage.objects.select_related('event').prefetch_related(
            'booths', 'schedules', 'galleries', 'highlights'
        )

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return ExpoVillageDetailSerializer
        return ExpoVillageListSerializer


class VillageBoothViewSet(viewsets.ModelViewSet):
    queryset = VillageBooth.objects.all()
    serializer_class = VillageBoothSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['village']

    def get_queryset(self):
        return VillageBooth.objects.select_related('village')


class VillageScheduleViewSet(viewsets.ModelViewSet):
    queryset = VillageSchedule.objects.all()
    serializer_class = VillageScheduleSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['village', 'day_number']


class VillageGalleryViewSet(viewsets.ModelViewSet):
    queryset = VillageGallery.objects.all()
    serializer_class = VillageGallerySerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['village', 'edition_year']


class VillageHighlightViewSet(viewsets.ModelViewSet):
    queryset = VillageHighlight.objects.all()
    serializer_class = VillageHighlightSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['village']


class EventHeroImageViewSet(viewsets.ModelViewSet):
    queryset = ExpoEventHeroImage.objects.all()
    serializer_class = HeroImageSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event']


class BoothApplicationViewSet(viewsets.ModelViewSet):
    queryset = BoothApplication.objects.all()
    serializer_class = BoothApplicationSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event', 'village', 'status']
    search_fields = ['company_name', 'email', 'reference_no']

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        app = self.get_object()
        serializer = BoothApplicationStatusUpdateSerializer(
            app, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(BoothStatusUpdateResponseSerializer(app).data)


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.select_related('event')
    serializer_class = RegistrationSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event', 'type', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'reference_no']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a registration and create a Speaker for SPEAKER applications."""
        registration = self.get_object()

        speaker = None
        if registration.type == Registration.RegType.SPEAKER:
            speaker = registration.create_speaker()

        registration.status = Registration.Status.APPROVED
        registration.save(update_fields=['status', 'updated_at'])

        return Response({
            'message': 'Registration approved.',
            'registration': RegistrationSerializer(registration, context={'request': request}).data,
            **(
                {'speaker': SpeakerSerializer(speaker, context={'request': request}).data}
                if speaker else {}
            ),
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a registration."""
        registration = self.get_object()
        registration.status = Registration.Status.REJECTED
        registration.save(update_fields=['status', 'updated_at'])
        return Response({
            'message': 'Registration rejected.',
            'registration': RegistrationSerializer(registration, context={'request': request}).data,
        })


class SpeakerViewSet(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event', 'is_confirmed']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Confirm a speaker."""
        speaker = self.get_object()
        speaker.is_confirmed = True
        speaker.save(update_fields=['is_confirmed', 'updated_at'])
        return Response(SpeakerSerializer(speaker, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def unconfirm(self, request, pk=None):
        """Unconfirm a speaker."""
        speaker = self.get_object()
        speaker.is_confirmed = False
        speaker.save(update_fields=['is_confirmed', 'updated_at'])
        return Response(SpeakerSerializer(speaker, context={'request': request}).data)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.select_related('event', 'speaker')
    serializer_class = SessionSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event', 'day_number', 'type']


class MediaAssetViewSet(viewsets.ModelViewSet):
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [IsBackofficeUser]
    filterset_fields = ['event', 'folder']
    search_fields = ['original_name', 'alt_text']

    def create(self, request, *args, **kwargs):
        import base64
        import uuid
        from django.core.files.base import ContentFile
        from PIL import Image
        import io

        folder = request.data.get('folder', 'misc')
        alt_text = request.data.get('altText', '')
        event_id = request.data.get('eventId')
        event = None
        if event_id:
            event = ExpoEvent.objects.filter(id=event_id).first()

        file_obj = None
        original_name = ''
        mime_type = ''
        size_bytes = 0
        width = None
        height = None

        # Handle base64 upload via JSON — accept both "file" and "file_base64" keys
        b64_data = request.data.get('file_base64') or request.data.get('file')
        if isinstance(b64_data, str) and b64_data.startswith('data:'):
            header, _, b64_content = b64_data.partition(',')
            mime_type = header.split(';')[0].split(':')[1] if ':' in header else 'image/png'
            ext = mime_type.split('/')[-1].split('+')[0]
            original_name = f'upload_{uuid.uuid4().hex[:8]}.{ext}'
            decoded = base64.b64decode(b64_content)
            size_bytes = len(decoded)
            file_obj = ContentFile(decoded, name=original_name)
        elif hasattr(b64_data, 'read'):
            file_obj = b64_data
            original_name = file_obj.name
            mime_type = getattr(file_obj, 'content_type', '') or ''
            size_bytes = file_obj.size
        else:
            return Response(
                {'success': False, 'error': 'No file provided. Send base64 string in "file_base64" or "file" field (data:image/...;base64,...) or multipart file.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get dimensions for images
        if mime_type.startswith('image/') and 'svg' not in mime_type:
            try:
                file_obj.seek(0)
                img = Image.open(io.BytesIO(file_obj.read()))
                width, height = img.size
                file_obj.seek(0)
            except Exception:
                pass

        asset = MediaAsset(
            event=event,
            original_name=original_name,
            file_name=original_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            folder=folder,
            alt_text=alt_text,
            width=width,
            height=height,
        )
        asset.file.save(original_name, file_obj, save=False)
        asset.save()

        return Response(
            MediaAssetSerializer(asset).data,
            status=status.HTTP_201_CREATED,
        )


# --- Public APIs ---

class LandingPageAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        event = (
            ExpoEvent.objects.filter(is_active=True, is_published=True)
            .prefetch_related('stats', 'focus_areas', 'partners', 'speakers', 'villages', 'hero_images')
            .first()
        )
        if not event:
            event = ExpoEvent.objects.filter(
                is_published=True, start_date__gte=timezone.now()
            ).order_by('start_date').first()
        if not event:
            return Response(
                {'success': False, 'error': 'No active or upcoming event found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(LandingPageResponseSerializer(event, context={'request': request}).data)


class EventEditionsAPIView(APIView):
    """Public endpoint listing all published event editions/years."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        events = ExpoEvent.objects.filter(
            is_published=True
        ).order_by('-year')
        data = []
        for e in events:
            data.append({
                'id': str(e.id),
                'year': e.year,
                'title': e.title,
                'tagline': e.tagline,
                'start_date': e.start_date,
                'end_date': e.end_date,
                'venue_name': e.venue_name,
                'is_current': e.is_active,
            })
        return Response({
            'success': True,
            'count': len(data),
            'current_year': next((e['year'] for e in data if e['is_current']), None),
            'editions': data,
        })


class VillagesListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        villages = ExpoVillage.objects.filter(event=event).order_by('order')
        return Response(VillagesListResponseSerializer({
            'count': villages.count(),
            'data': villages,
        }, context={'request': request}).data)


class VillageDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, year, slug):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        village = get_object_or_404(
            ExpoVillage.objects.select_related('event').prefetch_related(
                'booths', 'schedules', 'galleries', 'highlights'
            ),
            event=event, slug=slug,
        )
        return Response(VillageDetailResponseSerializer({
            'data': village,
        }, context={'request': request}).data)


class EventSpeakersAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        speakers = Speaker.objects.filter(
            event=event, is_confirmed=True
        ).order_by('order')
        return Response(SpeakersResponseSerializer({
            'count': speakers.count(),
            'data': speakers,
        }, context={'request': request}).data)


class EventScheduleAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        return Response(ScheduleResponseSerializer(event).data)


class RegisterGuestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        serializer = GuestRegistrationSerializer(
            data=request.data, context={'event': event}
        )
        serializer.is_valid(raise_exception=True)
        reg = serializer.save()
        return Response(
            RegistrationResponseSerializer(reg).data,
            status=status.HTTP_201_CREATED,
        )


class RegisterSpeakerAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        serializer = SpeakerRegistrationSerializer(
            data=request.data, context={'event': event}
        )
        serializer.is_valid(raise_exception=True)
        reg = serializer.save()
        return Response(
            RegistrationResponseSerializer(reg).data,
            status=status.HTTP_201_CREATED,
        )


class RegisterVolunteerAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        serializer = VolunteerRegistrationSerializer(
            data=request.data, context={'event': event}
        )
        serializer.is_valid(raise_exception=True)
        reg = serializer.save()
        return Response(
            RegistrationResponseSerializer(reg).data,
            status=status.HTTP_201_CREATED,
        )


class RegisterBoothAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year, is_published=True)
        serializer = BoothPublicRegistrationSerializer(
            data=request.data, context={'event': event}
        )
        serializer.is_valid(raise_exception=True)
        app = serializer.save()
        return Response(
            BoothApplicationResponseSerializer(app).data,
            status=status.HTTP_201_CREATED,
        )


# --- Admin dashboard & exports ---

class AdminMetricsAPIView(APIView):
    permission_classes = [IsBackofficeUser]

    def get(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year)
        return Response(AdminMetricsResponseSerializer(event).data)


class BadgeExportAPIView(APIView):
    permission_classes = [IsBackofficeUser]

    def get(self, request, year):
        event = get_object_or_404(ExpoEvent, year=year)
        reg_type = request.query_params.get('type', 'all')
        qs = Registration.objects.filter(event=event)
        if reg_type != 'all':
            qs = qs.filter(type=reg_type.upper())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="badges-{year}.csv"'
        writer = csv.writer(response)
        writer.writerow(['RefNo', 'Name', 'Email', 'Organization', 'Category', 'BadgeCode', 'Status'])
        for r in qs:
            writer.writerow([
                r.reference_no,
                f'{r.first_name} {r.last_name}',
                r.email,
                r.organization or '',
                r.type,
                r.badge_code,
                r.status,
            ])
        return response


class MediaLibraryAPIView(APIView):
    permission_classes = [IsBackofficeUser]

    def get(self, request):
        from rest_framework.pagination import PageNumberPagination

        folder = request.query_params.get('folder')
        search = request.query_params.get('search')
        event_id = request.query_params.get('eventId')
        qs = MediaAsset.objects.all()
        if folder and folder != 'all':
            qs = qs.filter(folder=folder)
        if event_id:
            qs = qs.filter(event_id=event_id)
        if search:
            qs = qs.filter(
                Q(original_name__icontains=search)
                | Q(alt_text__icontains=search)
            )
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('limit', 24))
        page = paginator.paginate_queryset(qs.order_by('-created_at'), request)
        return paginator.get_paginated_response(
            MediaAssetSerializer(page, many=True).data
        )

