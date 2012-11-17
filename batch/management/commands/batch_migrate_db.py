import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.migrate_db import MigrateDB


class Command(BaseCommand):
    args = "<host> <port> <user> <password> <db>"
    help = "migrates a db"

    def handle(self, *args, **options):
        if len(args) != 5:
            self.print_usage()
            exit(1)

        host = args[0]
        port = int(args[1])
        user = args[2]
        password = args[3]
        db = args[4]
        MigrateDB(host=host, port=port, user=user, password=password, db=db).start()

    def print_usage(self):
        print "usage: batch_migrate_db %s \n" % self.args
