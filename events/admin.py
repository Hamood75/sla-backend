from django.contrib import admin

from .models import (
    BoothApplication,
    EventStat,
    ExpoEvent,
    ExpoVillage,
    FocusArea,
    MediaAsset,
    Partner,
    Registration,
    Session,
    Speaker,
    VillageBooth,
    VillageGallery,
    VillageSchedule,
)


admin.site.register(ExpoEvent)
admin.site.register(EventStat)
admin.site.register(FocusArea)
admin.site.register(Partner)
admin.site.register(ExpoVillage)
admin.site.register(VillageBooth)
admin.site.register(VillageSchedule)
admin.site.register(VillageGallery)
admin.site.register(BoothApplication)
admin.site.register(Registration)
admin.site.register(Speaker)
admin.site.register(Session)
admin.site.register(MediaAsset)
