# -*- coding: utf-8 -*-
import sunburnt
from httplib2 import socket

from django.conf import settings

try:
    solr_interface = sunburnt.SolrInterface(settings.SOLR_URL)
except socket.error:
    solr_interface = None

def topic_to_doc(topic):
    doc = {
        "topic_id": topic.pk,
        "title": topic.title,
        "creator": topic.creator.username,
        "last_post_date": topic.last_post_date,
        "number_of_posts": topic.number_of_posts
    }
    return doc

class SolrSearcher(object):
    def index_topics(self, topics):
        docs = [topic_to_doc(t) for t in topics]
        solr_interface.add(docs)

    def search_topic(self, query, start, count):
        return solr_interface.query(title=query) \
            .sortby("-last_post_date") \
            .paginate(start=start, rows=count)

# create singleton class
SolrSearcher = SolrSearcher()
