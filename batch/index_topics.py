# -*- coding: utf-8 -*-
from django.core.paginator import Paginator, EmptyPage

from gfaqs.models import Topic
from batch.batch_base import Batch
from search.solr import SolrSearcher


CHUNK_SIZE=10000
class IndexTopics(Batch):
    """Indexes all topics in db into solr"""

    def start(self):
        qs = Topic.objects.all()
        paginator = Paginator(qs, CHUNK_SIZE)

        for i in range(1, paginator.num_pages):
            topics = paginator.page(i)
            SolrSearcher.index_topics(topics)
            for t in topics:
                print t.title
            break
