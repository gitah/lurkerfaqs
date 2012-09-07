import os
from datetime import datetime

from django.test import TestCase
from gfaqs.models import User, Board, Topic, Post
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
        except:
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
        topics = list(bs.retrieve())
        self.assertEquals(len(topics), 100)
        self.assertEquals(topics[0].title,"I love girls with big noses")
        self.assertEquals(topics[0].creator.username,"HeyJoeSchmoe")
        self.assertEquals(topics[49].title,"Brought my KKK knife to show and tell >_>")
        self.assertEquals(topics[49].creator.username,"Definfinite")
        self.assertEquals(topics[99].title,"The League of Shadows doesn't make any sense")
        self.assertEquals(topics[99].creator.username,"rattlesnake30")
        
class TopicScraperTest(TestCase):
    def setUp(self):
        self.path = "file://%s/examples/topics" % os.path.dirname(__file__)
        ot = Board(url="%s" % self.path, name="Other Titles")
        self.test_topic = Topic(board=ot, creator=User(username="foo"),
                title="tmp", gfaqs_id="b.html", status=0); 

    def test_parse_page(self):
        ts = TopicScraper(self.test_topic)
        posts = ts.parse_page(ts.get_page(0))
        self.assertEquals(len(posts),10)

        format_str = "%m/%d/%Y %I:%M:%S %p"

        p = posts[0]
        self.assertEquals(p.creator.username, "scarred_steak")
        self.assertEquals(p.post_num, "1")
        self.assertTrue(len(p.contents) > 1)
        self.assertFalse(p.signature)
        date = datetime.strptime("8/31/2012 11:56:28 PM", format_str)
        self.assertEquals(p.date.hour, date.hour)
        self.assertEquals(p.date.day, date.day)

        p = posts[9]
        self.assertEquals(p.creator.username, "Bako Ikporamee")
        self.assertEquals(p.post_num, "10")
        self.assertTrue(len(p.contents) > 1)
        self.assertTrue(p.signature)
        date = datetime.strptime("9/1/2012 6:58:08 AM", format_str)
        self.assertEquals(p.date.hour, date.hour)
        self.assertEquals(p.date.day, date.day)

    def test_retrieve(self):
        #TODO
        pass
