# -*- coding: utf-8 -*-
"""These tests are integration tests that hits the actual gfaqs website to make
sure the structure is compatible with the archiver"""

from django.conf import settings
from django.test import TestCase

from util.linkify import linkify
from util.linkify import YOUTUBE_HTML

class LinkifyTest(TestCase):

    def test_linkify(self):
        tests = [
            ('foo http://www.example.com bar', 'foo <a href="http://www.example.com">http://www.example.com</a> bar'),
            ('foo www.example.com bar', 'foo <a href="www.example.com">www.example.com</a> bar'),
            ('foo example.ca bar', 'foo <a href="example.ca">example.ca</a> bar'),
            ('foo example.com bar google.com', 'foo <a href="example.com">example.com</a> bar <a href="google.com">google.com</a>'),
            ('foo example.com/cow.jpg bar', 'foo <img src="example.com/cow.jpg" alt="external image"/> bar'),
            ('foo example.com bar example.com/cow.jpg', 'foo <a href="example.com">example.com</a> bar <img src="example.com/cow.jpg" alt="external image"/>'),
        ]

        for input, expected in tests:
            self.assertEquals(expected, linkify(input))

    def test_complicated(self):
        inp1 = 'care:<br/><br/>http://i48.tinypic.com/v2sqit.jpg</blockquote><br/><br/>Holy>care:<br/><br/>http://i48.tinypic.com/v2sqit.jpg</blockquote><br/><br/>Holy'
        inp2 = 'care:<br/><br/>i48.tinypic.ca/v2.jpg</blockquote><br/><br/>Holy>care:<br/><br/>i48.tinypic.ca/v2sqit.jpg</blockquote><br/><br/>Holy'
        self.assertEquals('care:<br/><br/><img src="http://i48.tinypic.com/v2sqit.jpg" alt="external image"/></blockquote><br/><br/>Holy>care:<br/><br/><img src="http://i48.tinypic.com/v2sqit.jpg" alt="external image"/></blockquote><br/><br/>Holy', linkify(inp1))
        self.assertEquals('care:<br/><br/><img src="i48.tinypic.ca/v2.jpg" alt="external image"/></blockquote><br/><br/>Holy>care:<br/><br/><img src="i48.tinypic.ca/v2sqit.jpg" alt="external image"/></blockquote><br/><br/>Holy', linkify(inp2)) 

    def test_youtube(self):
        youtube_vid = 'L8f5FvQZP0k'
        inp = 'http://www.youtube.com/watch?v=%s&feature=related' % youtube_vid
        self.assertEquals(YOUTUBE_HTML % youtube_vid, linkify(inp))
