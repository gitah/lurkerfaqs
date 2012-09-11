import sys
from django.core.management.base import BaseCommand, CommandError
from gfaqs.archiver import Archiver

PIDFILE="/var/run/gfaqs-archiver.pid"

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
            print "gfaqs-archiver started"
        elif args[0] == "stop":
            daemon.stop()
        elif args[0] == "restart":
            print "gfaqs-archiver stopped"
            daemon.restart()
            print "gfaqs-archiver restarted"
        else:
            print "unknown command"
            print help()
            sys.exit(2)
