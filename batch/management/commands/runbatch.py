import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import batch.top_users

def help():
    return "usage: python manage.py runbatch <batch_name>\n"

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Runs a batch'

    def handle(self, *args, **options):
        if len(args) != 1:
            print help()
            sys.exit(2)

        #create pid file
        if args[0] == "top_users":
            self.run_top_users()
        else:
            print "unknown batch"
            print help()
            sys.exit(2)

    def run_top_users(self):
      batch.top_users.TopUsersBatch().start()
