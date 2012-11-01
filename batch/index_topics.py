# -*- coding: utf-8 -*-
from django.core.paginator import Paginator

from gfaqs.models import Topic
from batch.batch_base import Batch
from search import Searcher


CHUNK_SIZE=10000

class IndexTopics(Batch):
    def start(self):
        all_topics = Topic.objects.all()
        paginator = Paginator(all_topics, 10000)

        for i in range(1, paginator.num_pages+1):
            topics = paginator.get_page(i)
            Searcher.index_topics(topics)
