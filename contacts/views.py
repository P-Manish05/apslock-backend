import os
import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
from .serializers import ContactSerializer
from .throttles import ContactRateThrottle
from newsletter.models import Subscriber


def send_contact_emails(contact):
    try:
        send_mail(
            subject=f"New Lead: {contact.name}",
            message=f"""
New contact form submission on APSLOCK website:

Name:     {contact.name}
Email:    {contact.email}
Company:  {contact.company or 'N/A'}
Message:  {contact.message}

Received at: {contact.created_at}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[os.getenv('NOTIFY_EMAIL')],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Owner email error: {e}")

    try:
        send_mail(
            subject=f"Hey {contact.name}, We got your message!",
            message=f"""
Hi {contact.name},

Thank you for reaching out to APSLOCK!

We've received your message and our team will
get back to you within 24 hours.

Message received:
─────────────────────────────
{contact.message}
─────────────────────────────

While you wait, feel free to explore our work:
https://demo2-alpha-ivory.vercel.app

Talk soon,
Team APSLOCK
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"User email error: {e}")


class ContactView(APIView):
    throttle_classes = [ContactRateThrottle]

    def get(self, request):
        contacts = Contact.objects.all().order_by('-created_at')
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)

        if serializer.is_valid():
            contact = serializer.save()

            # Auto subscribe user to newsletter
            try:
                subscriber, created = Subscriber.objects.get_or_create(
                    email=contact.email
                )

                # Send newsletter welcome email only if new subscriber
                if created:
                    send_mail(
                        subject="Welcome to APSLOCK!",
                        message=f"""
Hey there,

You're now subscribed to APSLOCK updates!

You'll be the first to know about:
- New services and offerings
- Industry insights
- Case studies and success stories
- Exclusive tips for growing your business

We're glad to have you.

Talk soon,
Team APSLOCK
https://demo2-alpha-ivory.vercel.app
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[contact.email],
                        fail_silently=False,
                    )

            except Exception as e:
                print(f"Newsletter subscribe error: {e}")

            # Send contact emails in background
            thread = threading.Thread(
                target=send_contact_emails,
                args=(contact,)
            )
            thread.daemon = True
            thread.start()

            return Response(
                {
                    "message": "Message received! We'll get back to you soon."
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )