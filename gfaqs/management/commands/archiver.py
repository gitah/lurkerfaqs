import sys
from django.core.management.base import BaseCommand, CommandError
from gfaqs.archiver import Archiver
from django.conf import settings

PIDFILE=settings.GFAQS_ARCHIVER_PID_FILE

def help():
    return "usage: python manage.py archiver [start|stop|restart]\n"

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Starts the Gamefaqs archiver'

    def handle(self, *args, **options):
        if len(args) != 1:
            print help()
            sys.exit(2)

        daemon = Archiver(pidfile=PIDFILE)
        #create pid file
        if args[0] == "start":
            try:
                daemon.start()
            except IOError:
                print "unable to write pid file %s" % PIDFILE
                sys.exit(2)
        elif args[0] == "stop":
            daemon.stop()
        elif args[0] == "restart":
            daemon.restart()
        else:
            print "unknown command"
            print help()
            sys.exit(2)
