# -*- coding: utf-8 -*-
from datetime import datetime

from mock import patch
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from gfaqs.models import User, Board, Topic, Post
from gfaqs.client import GFAQSClient
from gfaqs.scraper import BoardScraper, TopicScraper
from gfaqs.archiver import Archiver

TEST_BOARD = Board(
        url="localhost:8080/board/",
        name="Test Board",
        alias='foobar')

TEST_USER = User(username="foo")

TEST_TOPIC = Topic(
        board=TEST_BOARD,
        creator=TEST_USER,
        title="Test Topic",
        gfaqs_id=9999,
        number_of_posts=10,
        last_post_date = datetime.now(),
        status=0)

TEST_POST = Post(
        topic=TEST_TOPIC,
        creator=TEST_USER,
        date=datetime.now(),
        post_num=1,
        contents="Hello World",
        signature="Test Signature",
        status=Post.NORMAL)

class MockBoardScraper(object):
    def __init__(self, *args):
        TEST_BOARD.save()
        TEST_TOPIC.board = TEST_BOARD
        self.topics = [TEST_TOPIC]

    def retrieve(self):
        for topic in self.topics:
            yield topic

    def scrape_page(self, page_num):
        if(page_num > 0):
            raise ValueError()
        return self.topics

class MockTopicScraper(object):
    def __init__(self, *args):
        TEST_BOARD.save()
        TEST_USER.save()
        TEST_TOPIC.board = TEST_BOARD
        TEST_TOPIC.creator = TEST_USER
        TEST_TOPIC.save()
        TEST_POST.topic = TEST_TOPIC
        TEST_POST.creator = TEST_USER
        self.posts = [TEST_POST]

    def retrieve(self):
        for post in self.posts:
            yield post

    def scrape_page(self, page_num):
        if(page_num > 0):
            raise ValueError()
        return self.posts

class ArchiverTest(TestCase):
    """ Unit test """
    def setUp(self):
        self.test_board = TEST_BOARD
        base_url = self.test_board.url
        board_info = [(self.test_board.url, self.test_board.name, 5)]
        gfaqs_client = GFAQSClient()
        self.archiver = Archiver(
                board_info=board_info, 
                base=base_url,
                pidfile="",
                gfaqs_client=gfaqs_client)

    @patch("gfaqs.archiver.BoardScraper", MockBoardScraper)
    def test_archive_board(self):
        self.archiver.archive_board(self.test_board, recursive=False)
        self.assertEquals(len(Topic.objects.all()), 1)

    @patch("gfaqs.archiver.TopicScraper", MockTopicScraper)
    def test_archive_topic(self):
        test_topic = TEST_TOPIC
        self.archiver.archive_topic(test_topic)
        self.assertEquals(len(Post.objects.all()), 1)

"""
class FooTest(TestCase):
    @override_settings(DEBUG=True)
    def test_foo(self):
        gfaqs_client = GFAQSClient()
        archiver = Archiver(gfaqs_client=gfaqs_client)

        b = Board(
            url="http://www.gamefaqs.com/boards/2000121-anime-and-manga-other-titles",
            name="OT",
            alias="foo")
        b.save()
        user = User(username='lkasdjflk')
        user.save()
        t = Topic(board=b,
                creator=user,
                gfaqs_id=69003129,
                title="foo",
                number_of_posts=22,
                last_post_date=datetime.now(),
                status=Topic.NORMAL)
        t.save()
        archiver.archive_topic(t)
"""
