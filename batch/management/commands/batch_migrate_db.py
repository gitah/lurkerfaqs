import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.migrate_db import MigrateDB

def help():
    return "usage: python manage.py runbatch <batch_name>\n"

class Command(BaseCommand):
    args = ""
    help = "migrates a db"

    def handle(self, *args, **options):
        if len(args) != 4:
            "%s <host> <port> <user> <password>" % self.help()
        host = args[0]    
        port = args[1]    
        user = args[2]    
        password = args[3]    
        MigrateDB().start()
