import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.top_users import TopUsersBatch

def help():
    return "usage: python manage.py runbatch <batch_name>\n"

class Command(BaseCommand):
    args = ''
    help = 'Runs a batch to find the users with the most posts and topics'

    def handle(self, *args, **options):
        TopUsersBatch.start()
