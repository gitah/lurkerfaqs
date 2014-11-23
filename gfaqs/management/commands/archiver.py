# -*- coding: utf-8 -*-
import sys
import os
import logging

from django.core.management.base import BaseCommand, CommandError
from gfaqs.archiver import Archiver
from gfaqs.client import GFAQSClient
from gfaqs.client import AuthenticatedGFAQSClient
from django.conf import settings

PIDFILE=settings.GFAQS_ARCHIVER_PID_FILE

logger = logging.getLogger(settings.ARCHIVER_LOGGER)

def help():
    return "usage: python manage.py archiver [start|stop|restart|status]\n"

def log_start():
    logger.info("Starting archiver daemon")

def log_end():
    logger.info("Stopping archiver daemon")

def show_status():
    if os.path.isfile(PIDFILE):
        with open(PIDFILE) as fp:
            pid = fp.readlines()[0].strip()
            print "archiver running, process %s" % pid
    else:
        print "archiver stopped"

class Command(BaseCommand):
    args = '[start|stop|restart|status]'
    help = 'Starts the Gamefaqs archiver'

    def handle(self, *args, **options):
        if len(args) != 1:
            print help()
            sys.exit(2)

        if settings.GFAQS_LOGIN_AS_USER:
            gfaqs_client = AuthenticatedGFAQSClient(
                settings.GFAQS_LOGIN_EMAIL,
                settings.GFAQS_LOGIN_PASSWORD)
        else:
            gfaqs_client = GFAQSClient

        daemon = Archiver(pidfile=PIDFILE,
                gfaqs_client=gfaqs_client)
        #create pid file
        if args[0] == "start":
            try:
                log_start()
                daemon.start()
            except IOError:
                print "unable to write pid file %s" % PIDFILE
                sys.exit(2)

        elif args[0] == "stop":
            daemon.stop()
            log_end()

        elif args[0] == "restart":
            daemon.restart()

        elif args[0] == "status":
            show_status()

        else:
            print "unknown command"
            print help()
            sys.exit(2)
