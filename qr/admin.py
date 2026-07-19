from django.contrib import admin

from .models import QRCode, QRCodeAnalytics, QRCodeLink


class QRCodeLinkInline(admin.TabularInline):
    model = QRCodeLink
    extra = 1


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'owner', 'destination_type', 'is_active', 'scan_count', 'created_at']
    list_filter = ['destination_type', 'is_active', 'theme']
    search_fields = ['code', 'title', 'slug']
    readonly_fields = ['scan_count', 'created_at', 'updated_at']
    inlines = [QRCodeLinkInline]


@admin.register(QRCodeAnalytics)
class QRCodeAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['qr', 'device', 'browser', 'country', 'city', 'is_returning', 'timestamp']
    list_filter = ['device', 'browser', 'country', 'is_returning']
    search_fields = ['qr__code', 'city', 'country']
    readonly_fields = ['timestamp']
