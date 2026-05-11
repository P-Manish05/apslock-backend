from rest_framework import serializers
from .models import Availability, Booking


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = [
            'id',
            'date',
            'start_time',
            'end_time',
            'is_booked'
        ]


class BookingSerializer(serializers.ModelSerializer):
    availability_detail = AvailabilitySerializer(
        source='availability',
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'availability',
            'availability_detail',
            'name',
            'email',
            'phone',
            'message',
            'status',
            'meeting_link',
            'created_at'
        ]