# -*- coding: utf-8 -*-
import os
import time
import urllib2

from datetime import datetime
from threading import Thread

from django.conf import settings
from django.test import TestCase

from gfaqs.models import User, Board, Topic, Post
from gfaqs.client import GFAQSClient
from gfaqs.scraper import BoardScraper, TopicScraper
from gfaqs.archiver import Archiver

from mock_gfaqs_client import MockGFAQSClient

class GFAQsTest(TestCase):
    def setUp(self):
        path = "http://localhost"
        self.ce = Board(url="%s/boards/ce" % path, name="ce")
        self.ot = Board(url="%s/boards/ot" % path, name="ot")
        self.test_topic1 = Topic(
            board=self.ce,
            number_of_posts=39,
            creator=User(username="foo"),
            title="test_topic1",
            gfaqs_id="67150473",
            last_post_date=datetime.now(),
            status=0
        );

        self.gfaqs_client = MockGFAQSClient()


class BoardScraperTest(GFAQsTest):
    def test_parse_page(self):
        bs = BoardScraper(self.ot)
        html = self.gfaqs_client.get_topic_list(self.ot, 0)
        ot0_tl = bs.parse_page(html)

        self.assertEquals(len(ot0_tl), 50)
        t = ot0_tl[0]
        self.assertEquals(t.creator.username, "PhazonDaxterII")
        self.assertEquals(t.gfaqs_id, "67159953")
        self.assertEquals(t.title, 'One Piece Legendary Q&A CLVIII: " Only one spot remains to be filled!!!"')

        t = ot0_tl[-1]
        self.assertEquals(t.creator.username, "Whose_the_Man")
        self.assertEquals(t.gfaqs_id, "67129946")
        self.assertEquals(t.title, "A Certain Scientific Railgun Chapter 62 *Spoilers*")

    def test_retrieve(self):
        bs = BoardScraper(self.ce)
        topics = list(bs.retrieve(self.gfaqs_client))
        self.assertEquals(len(topics), 150)
        self.assertEquals(topics[0].title,"So I have DOMS...should I go workout tomorrow if I'm still sore?")
        self.assertEquals(topics[0].creator.username,"ToasterStrudeI")
        self.assertEquals(topics[19].title,"Is there such thing as verbal sex?")
        self.assertEquals(topics[19].creator.username,"BrazenMD")


class TopicScraperTest(GFAQsTest):
    def test_parse_page(self):
        ts = TopicScraper(self.test_topic1)
        html = self.gfaqs_client.get_post_list(self.test_topic1, 0)
        posts = ts.parse_page(html)
        self.assertEquals(len(posts), 50)

        format_str = "%m/%d/%Y %I:%M:%S %p"

        p = posts[0]
        self.assertEquals(p.creator.username, "Roxas_Oblivion")
        self.assertEquals(p.post_num, "1")
        self.assertTrue(len(p.contents) > 1)
        self.assertTrue(p.signature)
        date = datetime.strptime("9/3/2013 6:24:13 AM", format_str)
        self.assertEquals(p.date.hour, date.hour)
        self.assertEquals(p.date.day, date.day)
        self.assertEquals(p.status, Post.NORMAL)

        p = posts[9]
        self.assertEquals(p.creator.username, "aak57")
        self.assertEquals(p.post_num, "10")
        self.assertTrue(len(p.contents) > 1)
        self.assertTrue(p.signature)
        date = datetime.strptime("9/3/2013 7:11:15 AM", format_str)
        self.assertEquals(p.date.hour, date.hour)
        self.assertEquals(p.date.day, date.day)
        self.assertEquals(p.status, Post.NORMAL)

    def test_retrieve(self):
        ts = TopicScraper(self.test_topic1)
        posts = list(ts.retrieve(self.gfaqs_client))
        self.assertEquals(len(posts), 91)
        self.assertEquals(posts[0].creator.username, "Roxas_Oblivion")
        self.assertEquals(posts[-1].creator.username,"yamas11")


class ArchiverTest(GFAQsTest):

    def setUp(self):
        super(ArchiverTest,self).setUp()
        board_list = [(self.ce.url, self.ce.name, 5)]
        settings.GFAQS_LOGIN_AS_USER = False
        self.archiver = Archiver(board_info=board_list,
                gfaqs_client=self.gfaqs_client)

        class DaemonRunnerThread(Thread):
            def __init__(self, daemon):
                super(DaemonRunnerThread, self).__init__()
                self.daemon = daemon
                self.is_running = False

            def run(self):
                self.is_running = True
                self.daemon.start()

            def stop(self):
                if self.is_running:
                    self.daemon.stop()
                    self.is_running=False
        self.archiver_th = DaemonRunnerThread(self.archiver)

    def test_archive_board(self):
        self.ce.save()
        self.archiver.archive_board(self.ce, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 50)
        # run again to make sure we don't dupe
        self.archiver.archive_board(self.ce, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 50)

    def test_archive_topic(self):
        self.ce.save()
        creator=User(username="foo")
        creator.save()
        test_topic = Topic(
            board=self.ce,
            number_of_posts=129,
            creator=creator,
            title="tmp",
            gfaqs_id="67181037",
            last_post_date=datetime.now(),
        status=0);
        test_topic.save()

        self.archiver.archive_topic(test_topic)
        self.assertEquals(len(Post.objects.all()), 129)
        # run again to make sure we don't dupe
        self.archiver.archive_topic(test_topic)
        self.assertEquals(len(Post.objects.all()), 129)

    def tearDown(self):
        # we need this incase test_daemon crashes in the middle
        self.archiver_th.stop()

    def test_daemon(self):
        """ Test that the archiver daemon archives boards in the background

        Note: this test is tricky; the daemon runs on a seperate thread forever
            - we wait for a bit until Daemon finishes scraping and test db
        """
        self.archiver_th.start()

        # wait a while for archiver to do its thing
        time.sleep(30)

        self.assertEquals(len(Board.objects.all()), 1)
        # ensure pid file present
        try:
            open(settings.GFAQS_ARCHIVER_PID_FILE)
        except IOError:
            self.fail("pid file not found")

        self.assertEquals(len(Topic.objects.all()), 50)
        self.assertTrue(len(Post.objects.all()) > 100)

        self.archiver_th.stop()

        # ensure pid file gone
        try:
            open(settings.GFAQS_ARCHIVER_PID_FILE)
            self.fail("pid file still exists")
        except IOError:
            pass