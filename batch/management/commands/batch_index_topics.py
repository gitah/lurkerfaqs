import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.index_topics import IndexTopics

class Command(BaseCommand):
    args = ''
    help = 'Runs a batch to find the number of posts and topics made by each user'

    def handle(self, *args, **options):
        IndexTopics().start()
