# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, EmptyPage
from django.db import connection, transaction

from gfaqs.models import Topic, UnindexedTopic
from batch.batch_base import Batch
from search.solr import SolrSearcher


CHUNK_SIZE=10000

def print_progress(i, total):
    print "Progress: %.2f%s (%s/%s)" % (i * 100.0 / total, '%', i, total)

class IndexTopics(Batch):
    """Indexes all topics in db into solr"""

    def all(self):
        qs = Topic.objects.all()
        self._index(qs)

    @transaction.commit_on_success
    def update(self):
        qs = UnindexedTopic.objects.all()
        self._index([ut.topic for ut in qs])
        UnindexedTopic.objects.all().delete()

    def _index(self, qs):
        paginator = Paginator(qs, CHUNK_SIZE)
        total = paginator.num_pages

        for i in range(1, total+1):
            topics = paginator.page(i)
            SolrSearcher.index_topics(topics)
            print '\n'.join([t.title for t in topics])
            print_progress(i, total)
