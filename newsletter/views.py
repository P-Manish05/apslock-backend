import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscriber
from .serializers import SubscriberSerializer
from .throttles import NewsletterRateThrottle


class NewsletterView(APIView):
    throttle_classes = [NewsletterRateThrottle]

    def get(self, request):
        subscribers = Subscriber.objects.filter(is_active=True)
        serializer = SubscriberSerializer(subscribers, many=True)
        return Response(serializer.data)

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already subscribed
        if Subscriber.objects.filter(email=email).exists():
            return Response(
                {"message": "You're already subscribed!"},
                status=status.HTTP_200_OK
            )

        serializer = SubscriberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Welcome email to subscriber
            try:
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
https://apslock-website.vercel.app
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Newsletter email error: {e}")

            # Notify owner
            try:
                send_mail(
                    subject=f"New Subscriber: {email}",
                    message=f"""
New newsletter subscriber:

Email: {email}

Total active subscribers: {Subscriber.objects.filter(is_active=True).count()}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[os.getenv('NOTIFY_EMAIL')],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Owner notification error: {e}")

            return Response(
                {"message": "Successfully subscribed!"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )