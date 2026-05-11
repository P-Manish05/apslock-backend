from rest_framework.throttling import AnonRateThrottle

class NewsletterRateThrottle(AnonRateThrottle):
    scope = 'newsletter'