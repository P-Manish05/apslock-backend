import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Availability, Booking
from .serializers import AvailabilitySerializer, BookingSerializer
from .google_meet import create_google_meet
from .calendar_invite import generate_ics


class AvailabilityView(APIView):

    def get(self, request):
        slots = Availability.objects.filter(is_booked=False)
        serializer = AvailabilitySerializer(slots, many=True)
        return Response(serializer.data)


class BookingView(APIView):

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            availability_id = request.data.get('availability')

            # Check slot is still available
            try:
                slot = Availability.objects.get(
                    id=availability_id,
                    is_booked=False
                )
            except Availability.DoesNotExist:
                return Response(
                    {"error": "This slot is no longer available."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create Google Meet
            meet_link, event_id = create_google_meet(
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                attendee_name=request.data.get('name'),
                attendee_email=request.data.get('email'),
            )

            # Save booking
            booking = serializer.save(
                meeting_link=meet_link or ''
            )

            # Block the slot
            slot.is_booked = True
            slot.save()

            # Generate .ics file
            ics_content = generate_ics(
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                attendee_name=booking.name,
                attendee_email=booking.email,
                meet_link=meet_link or 'Link will be sent shortly'
            )

            # Send confirmation email with calendar invite
            try:
                email = EmailMessage(
                    subject="Your APSLOCK Consultation is Confirmed!",
                    body=f"""
Hi {booking.name},

Your free consultation call with APSLOCK is confirmed!

Details:
─────────────────────────────
Date:       {slot.date.strftime('%A, %d %B %Y')}
Time:       {slot.start_time.strftime('%I:%M %p')} IST
Duration:   45 minutes
Meet Link:  {meet_link or 'Will be sent shortly'}
─────────────────────────────

What to expect:
- Our team will understand your requirements
- We'll show you exactly how we can help
- Completely free, no obligations

The calendar invite is attached to this email.
Add it to your calendar to get a reminder.

See you on the call!
Team APSLOCK
https://apslock-website.vercel.app
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking.email],
                )

                email.attach(
                    'consultation.ics',
                    ics_content,
                    'text/calendar'
                )
                email.send()

            except Exception as e:
                print(f"Booking email error: {e}")

            # Notify owner
            try:
                EmailMessage(
                    subject=f"New Booking: {booking.name}",
                    body=f"""
New consultation booking:

Name:     {booking.name}
Email:    {booking.email}
Phone:    {booking.phone or 'N/A'}
Date:     {slot.date.strftime('%A, %d %B %Y')}
Time:     {slot.start_time.strftime('%I:%M %p')} IST
Message:  {booking.message or 'N/A'}
Meet:     {meet_link or 'N/A'}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[os.getenv('NOTIFY_EMAIL')],
                ).send()
            except Exception as e:
                print(f"Owner notification error: {e}")

            return Response(
                {
                    "message": "Consultation booked successfully!",
                    "meeting_link": meet_link,
                    "date": str(slot.date),
                    "time": str(slot.start_time)
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )