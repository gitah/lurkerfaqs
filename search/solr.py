# -*- coding: utf-8 -*-
import sunburnt
from httplib2 import socket

from django.conf import settings

from search.normalize import normalize_words

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
        solr_q =  solr_interface.query()
        for term in normalize_words(query.split()):
            solr_q = solr_q.query(title=term)

        resp = solr_q \
            .filter(board_alias=board_alias) \
            .sort_by("-last_post_date") \
            .paginate(start=start, rows=count) \
            .execute()
        return (resp.result.numFound, [result_to_gfaqs_id(t) for t in resp])

    def search_related_topics(self, topic, count):
        """Sends a request to solr for topics related to the given topic
        
        Returns up to count number of related topics
        Returns a list of topics
        """
        solr_q =  solr_interface.query()

        query_terms = normalize_words(topic.title.split())
        q_OR = solr_interface.Q(title="")
        for term in query_terms:
            q_OR |= solr_interface.Q(title=term)
        solr_q = solr_q.query(q_OR).exclude(id=topic.gfaqs_id)
        resp = solr_q.paginate(start=0, rows=count).execute()
        return [result_to_gfaqs_id(t) for t in resp]


# create singleton class
SolrSearcher = SolrSearcher()
