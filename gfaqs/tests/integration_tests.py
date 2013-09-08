# -*- coding: utf-8 -*-
"""These tests are integration tests that hits the actual gfaqs website to make
sure the structure is compatible with the archiver"""

from django.conf import settings
from django.test import TestCase

from gfaqs.models import User, Board, Topic, Post
from gfaqs.scraper import BoardScraper, TopicScraper
from gfaqs.client import GFAQSClient

CE = Board(url="%s/boards/400-current-events" % settings.GFAQS_URL, name="CE")
OT = Board(url="%s/boards/2000121-anime-and-manga-other-titles" % settings.GFAQS_URL, name="OT")

class GFAQsScrapeBoardTest(TestCase):
    """An integration test that hits an actual GameFAQs board checking if scraping
    works properly"""

    def test_scrape_board(self):
        """Test that we can still scrape topics and posts"""
        gfaqs_client = GFAQSClient()

        # scrape board
        bs = BoardScraper(OT)
        topic = bs.retrieve(gfaqs_client).next()
        self.assertTrue(topic)
        self.assertTrue(topic.title)
        self.assertTrue(topic.creator.username)

        # scrape topic
        ts = TopicScraper(topic)
        post = ts.retrieve(gfaqs_client).next()
        self.assertTrue(post)
        self.assertTrue(post.contents)
        self.assertTrue(post.creator.username)

class GFAQSLoginTest(TestCase):
    """ TODO """
    def test_login(self):
        """Test that we can still login to GameFAQs."""
        if not settings.GFAQS_LOGIN_AS_USER:
            return
        opener = authenticate(settings.GFAQS_LOGIN_EMAIL, settings.GFAQS_LOGIN_PASSWORD)

        # see that we can see topics on CE
        bs = BoardScraper(CE)
        topic = bs.retrieve(opener).next()
        self.assertTrue(topic)
        self.assertTrue(topic.title)
        self.assertTrue(topic.creator.username)
