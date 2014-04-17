# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import skip

from mock import patch
from django.conf import settings
from django.test import TestCase

from gfaqs.client import GFAQSClient, AuthenticatedGFAQSClient
from gfaqs.models import User, Board, Topic, Post
from gfaqs.scraper import BoardScraper, TopicScraper


GFAQS_BASE_URL = "http://www.gamefaqs.com"
GFAQS_BOARD_BASE = "http://www.gamefaqs.com/boards"
GFAQS_BOARD_URL = "%s/2000121-anime-and-manga-other-titles" % GFAQS_BOARD_BASE

class BoardScraperTest(TestCase):
    def setUp(self):
        path = GFAQS_BOARD_URL
        self.test_board = Board(url= path, name="Other Titles")
        self.gfaqs_client = GFAQSClient()

    def test_scrape_page(self):
        bs = BoardScraper(self.test_board, self.gfaqs_client)
        topics = bs.scrape_page(0)
        self.assertTrue(len(topics) > 1)


class TopicScraperTest(TestCase):
    def setUp(self):
        gfaq_topic_id = 68960382;
        test_board = Board(url=GFAQS_BOARD_URL, name="OT")

        self.test_topic = Topic(
            board=test_board,
            creator=User(username="foo"),
            title="tmp",
            gfaqs_id=gfaq_topic_id,
            status=0);

        self.gfaqs_client = GFAQSClient()

    def test_scrape_page(self):
        ts = TopicScraper(self.test_topic, self.gfaqs_client)
        posts = ts.scrape_page(0)
        self.assertTrue(len(posts) > 1)


class GFAQSAuthenticationTest(TestCase):
    def test_login(self):
        """Test that we can still login to GameFAQs."""
        if not settings.GFAQS_LOGIN_AS_USER:
            self.fail("Must enable login")
        ce = Board(
            url="%s/boards/400-current-events" % settings.GFAQS_URL, 
            name="CE")
        gfaqs_client = AuthenticatedGFAQSClient(
            settings.GFAQS_LOGIN_EMAIL,
            settings.GFAQS_LOGIN_PASSWORD)

        # see that we can see topics on CE
        bs = BoardScraper(ce, gfaqs_client)
        topics = bs.scrape_page(0)
        self.assertTrue(topics[0])
        self.assertTrue(topics[0].title)
        self.assertTrue(topics[0].creator.username)

