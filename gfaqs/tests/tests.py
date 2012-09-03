import os

from django.test import TestCase
from gfaqs.models import Board, Topic, Post
from gfaqs.scraper import BoardScraper, TopicScraper

class BoardScraperTest(TestCase):
    def setUp(self):
        self.path = "file://%s/examples/boards" % os.path.dirname(__file__)
        self.ce = Board(url="%s/ce.html" % self.path, name="Current Events")
        self.ot = Board(url="%s/ot.html" % self.path, name="Other Titles")

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
        except IOError:
            pass

    def test_parse_page(self):
        bs = BoardScraper(self.ot)
        
        ot0_tl = bs.parse_page(bs.get_page(0))
        self.assertEquals(len(ot0_tl), 50)
        t = ot0_tl[0]
        self.assertEquals(t.creator.username, "Hildetorr")
        self.assertEquals(t.gfaqs_id, "63892639")
        self.assertEquals(t.title, "Naruto 599 Very Heavy Spoilers")
        t = ot0_tl[-1]
        self.assertEquals(t.creator.username, "McDohl MR")
        self.assertEquals(t.gfaqs_id, "63892769")
        self.assertEquals(t.title, "Happy birthday Makoto Kikuchi! (THE iDOLM@STER, 8/29)")

        ot0_tl = bs.parse_page(bs.get_page(707))
        self.assertEquals(len(ot0_tl), 8)
        t = ot0_tl[4]
        self.assertEquals(t.creator.username, "jabini")
        self.assertEquals(t.gfaqs_id, "59271800")
        self.assertEquals(t.title, "Kyubei's true identity (spoiler)")

        try:
            # this page has no topics
            ot708_tl = bs.parse_page(bs.get_page(708))
        except ValueError:
            pass

    def test_retrieve(self):
        bs = BoardScraper(self.ce)
