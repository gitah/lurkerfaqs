# -*- coding: utf-8 -*-
import os

from gfaqs.client import GFAQSClient

"""
A mock for the GamefaqsClient for unit testing
"""

BASE_DIR = os.getcwd()
EXAMPLE_DIR = "%s/gfaqs/tests/examples" % BASE_DIR
BOARDS_DIR = "boards"
TOPICS_DIR = "topics"

class MockGFAQSClient(object):
    def __init__(self, email=None, password=None):
        pass

    def get_topic_list(self, board, pg):
        """Fetches the given topic list page from examples/"""
        fpath = "%s/%s/%s-%s.html" % (EXAMPLE_DIR, BOARDS_DIR, board.name, pg)
        try:
            with open(fpath) as fp:
                return fp.read()
        except IOError:
            raise ValueError("page not found")

    def get_post_list(self, topic, pg):
        """Fetches the given topic list page"""
        fpath = "%s/%s/%s-%s.html" % (EXAMPLE_DIR, TOPICS_DIR, topic.gfaqs_id, pg)
        try:
            with open(fpath) as fp:
                return fp.read()
        except IOError:
            raise ValueError("page not found")
