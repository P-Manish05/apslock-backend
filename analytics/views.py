from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from datetime import timedelta
from contacts.models import Contact
from bookings.models import Booking
from newsletter.models import Subscriber


class AnalyticsView(View):
    def get(self, request):
        today = timezone.now().date()
        this_week = timezone.now() - timedelta(days=7)
        this_month = timezone.now() - timedelta(days=30)

        # Leads (Contact submissions)
        total_leads = Contact.objects.count()
        leads_today = Contact.objects.filter(created_at__date=today).count()
        leads_this_week = Contact.objects.filter(created_at__gte=this_week).count()
        leads_this_month = Contact.objects.filter(created_at__gte=this_month).count()

        # Bookings
        total_bookings = Booking.objects.count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        cancelled_bookings = Booking.objects.filter(status='cancelled').count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        bookings_today = Booking.objects.filter(created_at__date=today).count()
        bookings_this_week = Booking.objects.filter(created_at__gte=this_week).count()

        # Newsletter
        total_subscribers = Subscriber.objects.count()
        active_subscribers = Subscriber.objects.filter(is_active=True).count()
        inactive_subscribers = Subscriber.objects.filter(is_active=False).count()
        subscribers_today = Subscriber.objects.filter(subscribed_at__date=today).count()
        subscribers_this_week = Subscriber.objects.filter(subscribed_at__gte=this_week).count()
        subscribers_this_month = Subscriber.objects.filter(subscribed_at__gte=this_month).count()

        data = {
            "leads": {
                "total": total_leads,
                "today": leads_today,
                "this_week": leads_this_week,
                "this_month": leads_this_month,
            },
            "bookings": {
                "total": total_bookings,
                "confirmed": confirmed_bookings,
                "cancelled": cancelled_bookings,
                "pending": pending_bookings,
                "today": bookings_today,
                "this_week": bookings_this_week,
            },
            "newsletter": {
                "total": total_subscribers,
                "active": active_subscribers,
                "inactive": inactive_subscribers,
                "today": subscribers_today,
                "this_week": subscribers_this_week,
                "this_month": subscribers_this_month,
            },
        }

        return JsonResponse(data)