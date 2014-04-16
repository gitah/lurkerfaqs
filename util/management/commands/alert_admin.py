# -*- coding: utf-8 -*-
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from util.alert import alert_admin


class Command(BaseCommand):
    args = 'subject msg'
    help = 'Sends an email to the configured administrator'

    def handle(self, *args, **options):
        if len(args) != 2:
            print "manage.py alert_admin <subject> <msg>"
            sys.exit(2)

        if not settings.EMAIL_HOST:
            print "Please configure SMTP settings (ex. EMAIL_HOST, EMAIL_PORT)"
            sys.exit(2)

        subject = args[0]
        msg = args[1]
        alert_admin(subject, msg)
