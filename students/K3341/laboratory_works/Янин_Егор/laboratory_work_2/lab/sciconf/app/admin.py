from django.contrib import admin
from .models import Location, Theme, Conference, TalkSubmission, ConferenceReview

admin.site.register(Location)
admin.site.register(Theme)
admin.site.register(Conference)
admin.site.register(TalkSubmission)
admin.site.register(ConferenceReview)