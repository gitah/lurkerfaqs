# -*- coding: utf-8 -*-
import os
import time
import urllib2

from datetime import datetime
from threading import Thread

from django.conf import settings
from django.test import TestCase
from gfaqs.models import User, Board, Topic, Post
from gfaqs.scraper import BoardScraper, TopicScraper
from gfaqs.client import GFAQSClient, AuthenticatedGFAQSClient
from gfaqs.archiver import Archiver

GFAQS_BOARD_PATH = "http://www.gamefaqs.com/boards/2000121-anime-and-manga-other-titles"

class BoardScraperTest(TestCase):
    def setUp(self):
        path = GFAQS_BOARD_PATH
        self.test_board = Board(url= path, name="Other Titles")
        self.gfaqs_client = GFAQSClient()

    def test_scrape_page(self):
        bs = BoardScraper(self.test_board, self.gfaqs_client)
        topics = bs.scrape_page(0)
        self.assertTrue(topics)


class TopicScraperTest(TestCase):
    def setUp(self):
        gfaq_topic_id = 68960382;
        test_board = Board(url=GFAQS_BOARD_PATH, name="OT")

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
        self.assertTrue(posts)


class GFAQSAuthenticationTest(TestCase):
    def test_login(self):
        """Test that we can still login to GameFAQs."""
        if not settings.GFAQS_LOGIN_AS_USER:
            return
        ce = Board(
            url="%s/boards/400-current-events" % settings.GFAQS_URL, 
            name="CE")
        gfaqs_client = AuthenticatedGFAQSClient()

        # see that we can see topics on CE
        bs = BoardScraper(ce, gfaqs_client)
        topics = bs.scrape_page(0)
        self.assertTrue(topics[0])
        self.assertTrue(topics[0].title)
        self.assertTrue(topics[0].creator.username)


class ArchiverTest(TestCase):
    class DaemonRunnerThread(Thread):
        def __init__(self,daemon):
            super(ArchiverTest.DaemonRunnerThread, self).__init__()
            self.daemon = daemon
            self.is_running = False

        def run(self):
            self.is_running = True
            self.daemon.start()

        def stop(self):
            if self.is_running:
                self.daemon.stop()
                self.is_running=False

    @classmethod
    def setUpClass(cls):
        cls.server_port = 14102
        cls.th = test_server.start_server(cls.server_port)

        path = GFAQS_BOARD_PATH
        board_list = [("boards/ce", "CE", 5)]
        settings.GFAQS_LOGIN_AS_USER = False
        cls.archiver = Archiver(board_info=board_list, base=path)
        cls.archiver_th = ArchiverTest.DaemonRunnerThread(cls.archiver)

    @classmethod
    def tearDownClass(cls):
        cls.archiver_th.stop()
        cls.th.stop()

    def test_archive_board(self):
        path = GFAQS_BOARD_PATH
        ce = Board(url="%s/boards/ce" % path, name="CE")
        ce.save()

        archiver = ArchiverTest.archiver
        archiver.archive_board(ce, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 20)
        archiver.archive_board(ce, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 20)

    def test_archive_topic(self):
        path = GFAQS_BOARD_PATH
        ot = Board(url="%s/boards/ot" % path, name="Other Titles")
        ot.save()
        creator=User(username="foo")
        creator.save()
        topic = Topic(board=ot, number_of_posts=57, creator=creator, title="tmp",
            gfaqs_id="64010226", last_post_date=datetime.now(), status=0);
        topic.save()

        archiver = ArchiverTest.archiver
        archiver.archive_topic(topic)
        self.assertEquals(len(Post.objects.all()), 57)
        archiver.archive_topic(topic)
        self.assertEquals(len(Post.objects.all()), 57)

    def test_daemon(self):
        ArchiverTest.archiver_th.start()

        # wait a while for archiver to do its thing
        time.sleep(5)
        self.assertEquals(len(Board.objects.all()), 1)
        # ensure pid file present
        try:
            open(settings.GFAQS_ARCHIVER_PID_FILE)
        except IOError:
            self.fail("pid file not found")

        self.assertEquals(len(Topic.objects.all()), 20)
        self.assertTrue(len(Post.objects.all()) > 200)
        ArchiverTest.archiver_th.stop()

        # ensure pid file gone
        try:
            open(settings.GFAQS_ARCHIVER_PID_FILE)
            self.fail("pid file still exists")
        except IOError:
            pass
