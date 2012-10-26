import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.migrate_db import MigrateDB


class Command(BaseCommand):
    args = "<host> <port> <user> <password>"
    help = "migrates a db"

    def handle(self, *args, **options):
        if len(args) != 4:
            self.print_usage()
            exit(1)

        host = args[0]
        port = int(args[1])
        user = args[2]
        password = args[3]
        MigrateDB(host=host, port=port, user=user, password=password).start()

    def print_usage(self):
        print "usage: batch_migrate_db %s \n" % self.args
