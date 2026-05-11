from django.urls import path
from .views import AvailabilityView, BookingView

urlpatterns = [
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('bookings/', BookingView.as_view(), name='bookings'),
]