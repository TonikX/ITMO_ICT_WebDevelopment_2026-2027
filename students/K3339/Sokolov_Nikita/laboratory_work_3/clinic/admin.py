from django.contrib import admin

from .models import (
    Cabinet,
    Doctor,
    MedicalCard,
    Patient,
    PriceList,
    User,
    Visit,
    WorkSchedule,
)

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(MedicalCard)
admin.site.register(Cabinet)
admin.site.register(PriceList)
admin.site.register(WorkSchedule)
admin.site.register(Visit)
