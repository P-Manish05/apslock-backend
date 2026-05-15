from django.urls import path
from .views import AvailabilityView, BookingView, BookedSlotsView

urlpatterns = [
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('bookings/', BookingView.as_view(), name='bookings'),
    path('booked-slots/', BookedSlotsView.as_view(), name='booked-slots'),
]