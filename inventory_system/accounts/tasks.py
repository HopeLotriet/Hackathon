# tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Subscriber

@shared_task
def send_subscription_confirmation_email(email):
    # Send confirmation email
    send_mail(
        'Subscription Confirmation',
        'Thank you for subscribing to FarmFresh! You will receive updates and promotions.',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

@shared_task
def send_notification_emails():
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        # Customize the email content here if needed
        email_content = render_to_string('email/notification_email.html', {'subscriber': subscriber})
        send_mail(
            'Notification',
            email_content,
            settings.EMAIL_HOST_USER,
            [subscriber.email],
            fail_silently=False,
        )
