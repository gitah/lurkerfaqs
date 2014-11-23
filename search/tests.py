"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime

from mock import patch

from django.test import TestCase
from gfaqs.models import Topic, User, Board
import search.solr



class SolrSearcherTest(TestCase):
    """Unit Tests for SolrSearcher """
    def setUp(self):
        board = Board(alias="foobar", url="a")
        user = User(username="pig")
        self.last_post_date = datetime.now()
        self.topic = Topic(topic_id="1234", title="my topic", creator=user,
            board=board, last_post_date=self.last_post_date,
            number_of_posts=10)

    def test_topic_to_doc(self):
        doc = search.solr.topic_to_doc(self.topic)
        #TODO assert doc contents
        pass

    def test_index_topics(self):
        with patch(search.solor.SolrSearcher, "index_topics") as mock:
            search.solr.SolrSearcher.index_topics([self.topic])
            #TODO: assert mock.return_val
        pass

    def test_search_topics(self):
        with patch(search.solor.SolrSearcher, "search_topic") as mock:
            #TODO
            search.solr.SolrSearcher.index_topics()
        pass
