import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from batch.index_topics import IndexTopics


def print_help_and_exit():
    print "./manage.py batch_index_topics (update|all)"
    exit(2)

class Command(BaseCommand):
    args = '(update|all)'
    help = 'Indexes topics to solr'

    def handle(self, *args, **options):
        if len(args) != 1:
            print_help_and_exit()

        if args[0] == "all":
            IndexTopics().all()
        if args[0] == "update":
            IndexTopics().update()
        else:
            print_help_and_exit()
