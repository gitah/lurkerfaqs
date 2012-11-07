import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.user_counts import UserCountBatch

def help():
    return "usage: python manage.py runbatch <batch_name>\n"

class Command(BaseCommand):
    args = ''
    help = 'Runs a batch to find the number of posts and topics made by each user'

    def handle(self, *args, **options):
        UserCountBatch().start()
