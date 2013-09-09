# -*- coding: utf-8 -*-
import sys

from django.conf import settings

from django.core.mail import send_mail

class EmailNotConfiguredException(Exception):
    pass

def alert_admin(subject, msg):
    if not settings.EMAIL_HOST:
        raise EmailNotConfiguredException("Please configure SMTP settings (ex. EMAIL_HOST, EMAIL_PORT)");

    admin_emails = [x[1] for x in settings.ADMINS]
    send_mail(subject, msg, 'alert@lurkerfaqs.com', admin_emails, fail_silently=False)
