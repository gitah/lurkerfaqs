import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.index_topics import IndexTopics

class Command(BaseCommand):
    args = ''
    help = 'Runs a batch to find the number of posts and topics made by each user'

    option_list = BaseCommand.option_list + (
        make_option('--update',
            action='store_true',
            dest='update',
            default=False,
            help='Indexes bizs that have not yet been indexed'),
        )

    def handle(self, *args, **options):
        if options['update']:
            IndexTopics().update()
        else:
            IndexTopics().start()
