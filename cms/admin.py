from django.contrib import admin

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
    HeroProgressBar,
    HeroSection,
    HeroTag,
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


class HeroTagInline(admin.TabularInline):
    model = HeroTag
    extra = 1


class HeroProgressInline(admin.TabularInline):
    model = HeroProgressBar
    extra = 1


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    inlines = [HeroTagInline, HeroProgressInline]


@admin.register(GallerySection)
class GallerySectionAdmin(admin.ModelAdmin):
    inlines = [GalleryImageInline]


admin.site.register(AnnouncementBar)
admin.site.register(NavItem)
admin.site.register(ImpactStat)
admin.site.register(AboutSection)
admin.site.register(BrandValue)
admin.site.register(Program)
admin.site.register(OrgChartNode)
admin.site.register(TeamMember)
admin.site.register(MeetingRequest)
admin.site.register(SocialLink)
admin.site.register(ContactMessage)
admin.site.register(NewsletterSubscriber)
admin.site.register(DonationTier)
admin.site.register(PaymentMethod)
admin.site.register(DonateModalCopy)
admin.site.register(Donation)
admin.site.register(Project)
admin.site.register(Event)
admin.site.register(Product)
admin.site.register(GalleryImage)

admin.site.site_header = 'Street Labs Africa Admin'
admin.site.site_title = 'SLA Backoffice'
admin.site.index_title = 'Digital Identity & CMS Platform'
