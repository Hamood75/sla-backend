from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve as static_serve
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from accounts.views import DepartmentViewSet, MeView, OrganizationViewSet, RegisterView, UserViewSet
from cms.views import (
    AboutSectionViewSet,
    AnnouncementBarViewSet,
    BrandValueViewSet,
    ContactMessageViewSet,
    DashboardStatsAPIView,
    DonateModalCopyView,
    DonationTierViewSet,
    DonationViewSet,
    EmailLogoView,
    EventViewSet,
    GalleryImageViewSet,
    GallerySectionViewSet,
    HeroSectionViewSet,
    HomepageAPIView,
    ImpactStatViewSet,
    MeetingRequestViewSet,
    NavItemViewSet,
    NewsletterSubscriberViewSet,
    OrgChartNodeViewSet,
    PaymentMethodViewSet,
    ProductViewSet,
    ProgramViewSet,
    ProjectViewSet,
    SiteSettingsView,
    SocialLinkViewSet,
    TeamMemberViewSet,
)
from profiles.views import EmployeeProfileViewSet
from qr.views import PlatformAnalyticsAPIView, QRCodeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'announcements', AnnouncementBarViewSet, basename='announcements')
router.register(r'nav', NavItemViewSet, basename='nav')
router.register(r'hero', HeroSectionViewSet, basename='hero')
router.register(r'stats', ImpactStatViewSet, basename='stats')
router.register(r'gallery', GallerySectionViewSet, basename='gallery')
router.register(r'gallery-images', GalleryImageViewSet, basename='gallery-images')
router.register(r'about', AboutSectionViewSet, basename='about')
router.register(r'values', BrandValueViewSet, basename='values')
router.register(r'programs', ProgramViewSet, basename='programs')
router.register(r'org-chart', OrgChartNodeViewSet, basename='org-chart')
router.register(r'team', TeamMemberViewSet, basename='team')
router.register(r'meeting-requests', MeetingRequestViewSet, basename='meeting-requests')
router.register(r'social-links', SocialLinkViewSet, basename='social-links')
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-messages')
router.register(r'newsletter', NewsletterSubscriberViewSet, basename='newsletter')
router.register(r'donation-tiers', DonationTierViewSet, basename='donation-tiers')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-methods')
router.register(r'donations', DonationViewSet, basename='donations')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'events', EventViewSet, basename='events')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'profiles', EmployeeProfileViewSet, basename='profiles')
router.register(r'qr', QRCodeViewSet, basename='qr')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/me/', MeView.as_view(), name='me'),
    path('api/cms/homepage/', HomepageAPIView.as_view(), name='homepage'),
    path('api/cms/email-logo/', EmailLogoView.as_view(), name='email-logo'),
    path('api/cms/settings/', SiteSettingsView.as_view(), name='site-settings'),
    path('api/cms/donate-copy/', DonateModalCopyView.as_view(), name='donate-copy'),
    path('api/dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('api/analytics/platform/', PlatformAnalyticsAPIView.as_view(), name='platform-analytics'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include(router.urls)),
]

# Always serve MEDIA (uploads). Production currently proxies to Django on :8000
# without a dedicated nginx media alias, and DEBUG=False disables django.conf.urls.static.
urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        static_serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
