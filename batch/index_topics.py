# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, EmptyPage

from gfaqs.models import Topic
from batch.batch_base import Batch
from search.solr import SolrSearcher


CHUNK_SIZE=10000

def print_progress(i, total):
    print "Progress: %.2f%s (%s/%s)" % (i * 100.0 / total, '%', i, total)

class IndexTopics(Batch):
    """Indexes all topics in db into solr"""

    def start(self):
        qs = Topic.objects.all()
        self._index(qs)

    def update(self):
        # get last indexed topic by date
        last_indexed_topic_gfaqs_id = SolrSearcher.get_last_indexed_topic()

        # index everything if we can't find any topics
        if not last_indexed_topic_gfaqs_id:
            self.start()
            return
        last_indexed_topic = Topic.objects.get(
            gfaqs_id=last_indexed_topic_gfaqs_id)

        # get topics > that last date
        qs = Topic.objects.filter(
            last_post_date__gte=last_indexed_topic.last_post_date)
        self._index(qs)

    def _index(self, qs):
        paginator = Paginator(qs, CHUNK_SIZE)
        total = paginator.num_pages

        for i in range(1, total+1):
            topics = paginator.page(i)
            SolrSearcher.index_topics(topics)
            print_progress(i, total)
