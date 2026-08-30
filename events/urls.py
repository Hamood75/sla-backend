from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminMetricsAPIView,
    BadgeExportAPIView,
    BoothApplicationViewSet,
    EventEditionsAPIView,
    EventHeroImageViewSet,
    EventScheduleAPIView,
    EventSpeakersAPIView,
    EventStatViewSet,
    ExpoEventViewSet,
    ExpoVillageViewSet,
    FocusAreaViewSet,
    LandingPageAPIView,
    MediaAssetViewSet,
    MediaLibraryAPIView,
    PartnerViewSet,
    RegisterBoothAPIView,
    RegisterGuestAPIView,
    RegisterSpeakerAPIView,
    RegisterVolunteerAPIView,
    RegistrationViewSet,
    SessionViewSet,
    SpeakerViewSet,
    VillageBoothViewSet,
    VillageDetailAPIView,
    VillageGalleryViewSet,
    VillageHighlightViewSet,
    VillagesListAPIView,
    VillageScheduleViewSet,
)

router = DefaultRouter()
router.register(r'admin/event-hero-images', EventHeroImageViewSet, basename='admin-event-hero-images')
router.register(r'admin/expo-events', ExpoEventViewSet, basename='admin-expo-events')
router.register(r'admin/event-stats', EventStatViewSet, basename='admin-event-stats')
router.register(r'admin/focus-areas', FocusAreaViewSet, basename='admin-focus-areas')
router.register(r'admin/partners', PartnerViewSet, basename='admin-partners')
router.register(r'admin/villages', ExpoVillageViewSet, basename='admin-expo-villages')
router.register(r'admin/village-booths', VillageBoothViewSet, basename='admin-village-booths')
router.register(r'admin/village-schedules', VillageScheduleViewSet, basename='admin-village-schedules')
router.register(r'admin/village-galleries', VillageGalleryViewSet, basename='admin-village-galleries')
router.register(r'admin/village-highlights', VillageHighlightViewSet, basename='admin-village-highlights')
router.register(r'admin/booth-applications', BoothApplicationViewSet, basename='admin-booth-applications')
router.register(r'admin/registrations', RegistrationViewSet, basename='admin-registrations')
router.register(r'admin/speakers', SpeakerViewSet, basename='admin-speakers')
router.register(r'admin/sessions', SessionViewSet, basename='admin-sessions')
router.register(r'admin/media-assets', MediaAssetViewSet, basename='admin-media-assets')

urlpatterns = [
    path('events/landing/', LandingPageAPIView.as_view(), name='events-landing'),
    path('events/editions/', EventEditionsAPIView.as_view(), name='events-editions'),
    path('events/<int:year>/villages/', VillagesListAPIView.as_view(), name='event-villages-list'),
    path('events/<int:year>/villages/<slug:slug>/', VillageDetailAPIView.as_view(), name='event-village-detail'),
    path('events/<int:year>/speakers/', EventSpeakersAPIView.as_view(), name='event-speakers'),
    path('events/<int:year>/schedule/', EventScheduleAPIView.as_view(), name='event-schedule'),
    path('events/<int:year>/register/guest/', RegisterGuestAPIView.as_view(), name='register-guest'),
    path('events/<int:year>/register/speaker/', RegisterSpeakerAPIView.as_view(), name='register-speaker'),
    path('events/<int:year>/register/volunteer/', RegisterVolunteerAPIView.as_view(), name='register-volunteer'),
    path('events/<int:year>/register/booth/', RegisterBoothAPIView.as_view(), name='register-booth'),
    path('admin/events/<int:year>/metrics/', AdminMetricsAPIView.as_view(), name='admin-event-metrics'),
    path('admin/events/<int:year>/export/badges/', BadgeExportAPIView.as_view(), name='admin-export-badges'),
    path('admin/files/', MediaLibraryAPIView.as_view(), name='admin-media-library'),
    path('', include(router.urls)),
]
