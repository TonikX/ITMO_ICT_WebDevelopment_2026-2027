from django.urls import path

from . import views

app_name = "hotel_app"
urlpatterns = [
    path("reports/quarterly/", views.QuarterlyReportView.as_view(), name="quarterly-report"),
    path("check-in/", views.CheckInView.as_view(), name="check-in"),
    path(
        "accommodations/<int:pk>/check-out/",
        views.CheckOutView.as_view(), name="check-out",
    ),
    path(
        "employees/<int:pk>/dismiss/",
        views.DismissEmployeeView.as_view(), name="employee-dismiss",
    ),
    path("room-types/", views.RoomTypeListCreateView.as_view(), name="room-type-list"),
    path("room-types/<int:pk>/", views.RoomTypeDetailView.as_view(), name="room-type-detail"),
    path("floors/", views.FloorListCreateView.as_view(), name="floor-list"),
    path("floors/<int:pk>/", views.FloorDetailView.as_view(), name="floor-detail"),
    path("rooms/", views.RoomListCreateView.as_view(), name="room-list"),
    path("rooms/<int:pk>/", views.RoomDetailView.as_view(), name="room-detail"),
    path("guests/", views.GuestListCreateView.as_view(), name="guest-list"),
    path("guests/<int:pk>/", views.GuestDetailView.as_view(), name="guest-detail"),
    path("employees/", views.EmployeeListCreateView.as_view(), name="employee-list"),
    path("employees/<int:pk>/", views.EmployeeDetailView.as_view(), name="employee-detail"),
    path("accommodations/", views.AccommodationListView.as_view(), name="accommodation-list"),
    path("accommodations/<int:pk>/", views.AccommodationDetailView.as_view(), name="accommodation-detail"),
    path("stays/", views.StayListView.as_view(), name="stay-list"),
    path("stays/<int:pk>/", views.StayDetailView.as_view(), name="stay-detail"),
    path("cleaning-schedules/", views.CleaningScheduleListView.as_view(), name="cleaning-schedule-list"),
    path("cleaning-schedules/<int:pk>/", views.CleaningScheduleDetailView.as_view(), name="cleaning-schedule-detail"),
    path("rooms/<int:pk>/accommodations/", views.RoomAccommodationsView.as_view(), name="room-accommodations"),
    path("employees/<int:pk>/schedule/", views.EmployeeScheduleView.as_view(), name="employee-schedule"),
    path(
        "analytics/room-guests/", views.RoomGuestsAnalyticsView.as_view(),
        name="analytics-room-guests",
    ),
    path(
        "analytics/guests-by-city/", views.GuestsByCityAnalyticsView.as_view(),
        name="analytics-guests-by-city",
    ),
    path(
        "analytics/guest-cleaner/", views.GuestCleanerAnalyticsView.as_view(),
        name="analytics-guest-cleaner",
    ),
    path(
        "analytics/available-rooms/", views.AvailableRoomsAnalyticsView.as_view(),
        name="analytics-available-rooms",
    ),
    path(
        "analytics/concurrent-guests/", views.ConcurrentGuestsAnalyticsView.as_view(),
        name="analytics-concurrent-guests",
    ),
]
