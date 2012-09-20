import os
import time
import urllib2

from datetime import datetime
from threading import Thread

from django.conf import settings
from django.test import TestCase
from gfaqs.models import User, Board, Topic, Post
from gfaqs.scraper import BoardScraper, TopicScraper
from gfaqs.archiver import Archiver

import test_server

EXAMPLE_DIR = "file://%s/examples" % os.path.dirname(__file__)
#start server

def start_server(port):
        server = test_server.create_server(port)
        server.serve_forever()

class BoardScraperTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_port = 14100
        cls.th = test_server.start_server(cls.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.th.stop()

    def setUp(self):
        path = "http://localhost:%s" % BoardScraperTest.server_port
        self.ce = Board(url="%s/boards/ce" % path, name="Current Events")
        self.ot = Board(url="%s/boards/ot" % path, name="Other Titles")

    def test_get_page(self):
        bs = BoardScraper(self.ce)
        try: 
            bs.get_page(0)
            bs.get_page(1)
        except IOError:
            self.fail("page not found")

        try:
            # should not exist
            bs.get_page(99999)
        except:
            pass

    def test_parse_page(self):
        bs = BoardScraper(self.ot)
        
        ot0_tl = bs.parse_page(bs.get_page(0))
        self.assertEquals(len(ot0_tl), 10)
        t = ot0_tl[0]
        self.assertEquals(t.creator.username, "EmeralDragon23")
        self.assertEquals(t.gfaqs_id, "64019288")
        self.assertEquals(t.title, "Here's my Cage of Eden prediction *spoilers*")
        t = ot0_tl[-1]
        self.assertEquals(t.creator.username, "Hellcopter")
        self.assertEquals(t.gfaqs_id, "64017353")
        self.assertEquals(t.title, 'What\'s anime really got you "into" anime?')

        try:
            # this page has no topics
            ot708_tl = bs.parse_page(bs.get_page(708))
        except ValueError:
            pass

    def test_retrieve(self):
        bs = BoardScraper(self.ce)
        topics = list(bs.retrieve())
        self.assertEquals(len(topics), 20)
        self.assertEquals(topics[0].title,"How do you keep yourself from lucid dreaming?")
        self.assertEquals(topics[0].creator.username,"hikaru_beoulve")
        self.assertEquals(topics[19].title,"What were/are you the biggest fan of, Rock Band or Guitar Hero")
        self.assertEquals(topics[19].creator.username,"Purecorruption")
        
class TopicScraperTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_port = 14101
        cls.th = test_server.start_server(cls.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.th.stop()

    def setUp(self):
        path = "http://localhost:%s" % TopicScraperTest.server_port
        ce = Board(url="%s/boards/ce" % path, name="Other Titles")
        self.test_topic = Topic(board=ce, creator=User(username="foo"),
                title="tmp", gfaqs_id="63995827", status=0);

    def test_parse_page(self):
        ts = TopicScraper(self.test_topic)
        posts = ts.parse_page(ts.get_page(0))
        self.assertEquals(len(posts),10)

        format_str = "%m/%d/%Y %I:%M:%S %p"

        p = posts[0]
        self.assertEquals(p.creator.username, "CoolBeansAvl")
        self.assertEquals(p.post_num, "1")
        self.assertTrue(len(p.contents) > 1)
        self.assertTrue(p.signature)
        date = datetime.strptime("9/9/2012 11:36:44 AM", format_str)
        self.assertEquals(p.date.hour, date.hour)
        self.assertEquals(p.date.day, date.day)
        self.assertEquals(p.status, Post.NORMAL)

        p = posts[9]
        self.assertEquals(p.creator.username, "stepalicious")
        self.assertEquals(p.post_num, "10")
        self.assertTrue(len(p.contents) > 1)
        self.assertTrue(p.signature)
        date = datetime.strptime("9/10/2012 7:11:39 AM", format_str)
        self.assertEquals(p.date.hour, date.hour)
        self.assertEquals(p.date.day, date.day)
        self.assertEquals(p.status, Post.NORMAL)

    def test_retrieve(self):
        ts = TopicScraper(self.test_topic)
        posts = list(ts.retrieve())
        self.assertEquals(len(posts), 53)
        self.assertEquals(posts[0].creator.username, "CoolBeansAvl")
        self.assertEquals(posts[-1].creator.username,"Xelltrix")

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

        path = "http://localhost:%s" % ArchiverTest.server_port
        board_list = [("boards/ce", "CE", 5)]
        cls.archiver = Archiver(board_info=board_list,base=path)
        cls.archiver_th = ArchiverTest.DaemonRunnerThread(cls.archiver)

    @classmethod
    def tearDownClass(cls):
        cls.archiver_th.stop()
        cls.th.stop()

    def test_archive_board(self):
        path = "http://localhost:%s" % ArchiverTest.server_port
        ce = Board(url="%s/boards/ce" % path, name="CE")
        ce.save()

        archiver = ArchiverTest.archiver
        archiver.archive_board(ce, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 20)
        archiver.archive_board(ce, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 20)
    
    def test_archive_topic(self):
        path = "http://localhost:%s" % ArchiverTest.server_port
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
        self.assertEquals(len(Post.objects.all()), 285)
        ArchiverTest.archiver_th.stop()

        # ensure pid file gone
        try:
            open(settings.GFAQS_ARCHIVER_PID_FILE)
            self.fail("pid file still exists")
        except IOError:
            pass
