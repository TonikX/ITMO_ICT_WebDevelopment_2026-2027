from django.contrib import admin
from .models import (
    CompanyType, Company, AircraftType, Aircraft, Airport, Route,
    Crew, Employee, Flight, TransitStop, CrewMember, Admission,
)

admin.site.register(CompanyType)
admin.site.register(Company)
admin.site.register(AircraftType)
admin.site.register(Aircraft)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Employee)
admin.site.register(Flight)
admin.site.register(TransitStop)
admin.site.register(CrewMember)
admin.site.register(Admission)