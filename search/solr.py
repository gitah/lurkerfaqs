# -*- coding: utf-8 -*-
import sunburnt
from httplib2 import socket

from django.conf import settings

solr_interface = sunburnt.SolrInterface(settings.SOLR_URL)

def topic_to_doc(topic):
    doc = {
        "id": topic.gfaqs_id,
        "title": topic.title,
        "creator": topic.creator.username,
        "last_post_date": topic.last_post_date,
        "number_of_posts": topic.number_of_posts,
        "board_alias": topic.board.alias,
    }
    return doc

def result_to_gfaqs_id(raw_topic):
    (gfaqs_id,) = raw_topic["id"]
    return gfaqs_id

class SolrSearcher(object):
    def index_topics(self, topics):
        docs = [topic_to_doc(t) for t in topics]
        solr_interface.add(docs)

    def search_topic(self, query, board_alias, start, count):
        """Sends a request to solr for topics matching query

        Returns a 2-tuple: (total_results, result_list)
        """
        resp = solr_interface.query(title=query) \
            .filter(board_alias=board_alias) \
            .sort_by("-last_post_date") \
            .paginate(start=start, rows=count) \
            .execute()
        return (resp.result.numFound, [result_to_gfaqs_id(t) for t in resp])

    def get_last_indexed_topic(self):
        resp = solr_interface.query().sort_by("-last_post_date").paginate(start=0, rows=1).execute()
        return [result_to_gfaqs_id(t) for t in resp][0]

# create singleton class
SolrSearcher = SolrSearcher()
