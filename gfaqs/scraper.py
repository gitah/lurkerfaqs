# -*- coding: utf-8 -*-
import urllib2
from urllib import urlencode
from urlparse import urlparse
from datetime import datetime

from bs4 import BeautifulSoup, element
from django.conf import settings

from gfaqs.util import strptime
from gfaqs.models import User, Board, Topic, Post
from gfaqs.client import GFAQSClient

TOPIC_STATUS_MAP = {
    "topic.gif": Topic.NORMAL,
    "lock.gif": Topic.CLOSED,
    "topic_poll.gif": Topic.POLL,
    "topic_poll_closed.gif": Topic.POLL_CLOSED,
    "topic_poll_archived.gif": Topic.POLL_ARCHIVED,
    "topic_archived.gif": Topic.ARCHIVED,
    "topic_closed.gif": Topic.CLOSED,
    "sticky.gif": Topic.STICKY,
    "sticky_closed.gif": Topic.STICKY_CLOSED,
}

STRING_EDITED = "(edited)";
STRING_MODDED = "[This message was deleted at the request of a moderator or administrator]";
STRING_CLOSED = "[This message was deleted at the request of the original poster]";

TOPIC_DATE_FORMAT_STR = "%m/%d %I:%M%p"
TOPIC_DATE_ALT_FORMAT_STR = "%m/%d/%Y"
POST_DATE_FORMAT_STR = "Posted %m/%d/%Y %I:%M:%S %p"

# <rage>
# The code below took me 3 hours to debug all because all because gfaqs is
# backwards as fuck. Yes I'm mad.
#
# Modern sites basically all use UTF-8 encoding, but no not gfaqs: the header
# and HTML says the page uses ISO-8859-1. This would be alright, but guess what?
# It turns out this is a big fat lie...
#</rage>
GFAQS_ENCODING="windows-1252"

def generate_query_string(page):
    """Returns a query string for a URL to a board or topic"""
    query = {
        "page": page,
        "results": 1,  #display poll results
    }
    return urlencode(query)

class Scraper(object):
    def retrieve(self, gfaqs_client):
        """generator that returns the next object the scraper will scrape"""
        # implement in subclass
        raise NotImplementedError()

    def parse_page(self, html):
        # implement in subclass
        raise NotImplementedError()

    def base_url(self):
        # implement in subclass
        raise NotImplementedError()


class BoardScraper(Scraper):
    def __init__(self, board):
        self.board = board

    def retrieve(self, gfaqs_client):
        pg = 0
        while True:
            try:
                html = gfaqs_client.get_topic_list(board, pg)
                for topic in self.parse_page(html):
                    yield topic
                pg += 1
            except ValueError:
                break
    
    def parse_page(self, html):
        """ parses the page and returns a list of Topic objects

            DOM Layout of a board
            <table class="board topics">
                <tr>
                    <td>status img</td>
                    <td>link to topic</td>
                    <td>creator</td>
                    <td>post count</td>
                    <td>last post date</td>
                </tr>
                ...
            </table>
        """
        soup = BeautifulSoup(html, from_encoding=GFAQS_ENCODING)
        topics = []

        topic_table = soup.find("table", class_="board topics")
        if not topic_table:
            raise ValueError("Page contains no posts")
        topic_tags = topic_table.find_all("tr")

        for topic_tag in topic_tags:
            tds = topic_tag.find_all("td")
            if not tds:
                continue
            assert len(tds) == 5, "Topic html invalid format (%s)" % self.base_url()

            status_img = tds[0].img["src"].split("/")[-1]
            topic_status = TOPIC_STATUS_MAP.get(status_img, None)
            assert topic_status != None, "status image %s not found (%s)" % (status_img, self.base_url())

            topic_gfaqs_id = tds[1].a["href"].split("/")[-1]
            topic_title = tds[1].a.text

            # we split because username might have (M) at the end
            username = tds[2].text.split()
            if "(M)" in username[-1]:
                username = username[:-1]
            username = ' '.join(username)
            creator = User(username=username)
            post_count = int(tds[3].text)

            try:
                date_raw = tds[4].a.text
                dt = strptime(date_raw, TOPIC_DATE_FORMAT_STR)
                # the year is not sepcified on gfaqs, 
                # so I'll set it to the current year
                curr_year = datetime.now().year
                dt = datetime(curr_year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            except ValueError:
                # archived topic, use alternative format str
                dt = strptime(date_raw, TOPIC_DATE_ALT_FORMAT_STR)

            topic = Topic(board=self.board, creator=creator, 
                    gfaqs_id=topic_gfaqs_id, title=topic_title,
                    number_of_posts=post_count, last_post_date=dt, 
                    status=topic_status)
            topics.append(topic)

        return topics


class TopicScraper(Scraper):
    def __init__(self, topic):
        self.topic = topic

    def retrieve(self, gfaqs_client):
        pg = 0
        while True:
            try:
                html = gfaqs_client.get_post_list(self.topic, pg)
                for topic in self.parse_page(html):
                    yield topic
                pg += 1
            except ValueError:
                break

    def parse_page(self, html):
        """ parses the page and returns a list of Post objects 

            DOM Layout of a topic
            <table class="board messages">
            <tr>
               <td class="author">
                   - username
                   - post date
               </td>
               <td>
                   <div class="msg_body">
                       post contents
                       <br>---<br>
                       Signature
                   </div>
               </td>
            </tr> 
        """
        soup = BeautifulSoup(html, from_encoding=GFAQS_ENCODING)
        posts = []
        post_table = soup.find("table", class_="board message")
        if not post_table:
            raise ValueError("Page contains no posts")

        post_tags = post_table.find_all("tr")
        for tr in post_tags:
            tds = tr.find_all("td")
            if not tds:
                continue
            assert len(tds) == 2, "post html invalid format (%s)" % self.base_url()

            postinfo = list(tds[0].div.children)
            post_status = Post.NORMAL
            for el in postinfo:
                if type(el) == element.NavigableString:
                    if el.string.startswith("Posted"):
                        date_raw = " ".join(el.string.split())
                        dt = strptime(date_raw,POST_DATE_FORMAT_STR)
                    elif el.string == STRING_EDITED:
                        post_status = Post.EDITED
                elif el.get("name"):
                    post_num = el["name"]
                elif el.get("class") and el.get("class")[0] == "name":
                    poster = el.text

            comps = list(tds[1].div.children)
            contents = []
            i = 0
            while i < len(comps):
                comp = comps[i]
                # parse until we reach signature
                if hasattr(comp, "name") and comp.name == "br" and i+2 < len(comps):
                    if comps[i+1] == "---":
                        break 
                contents.append(comp)
                i += 1

            signature = []
            i += 3
            while i < len(comps):
                signature.append(comps[i])
                i += 1

            content_text = "".join([unicode(x) for x in contents])
            signature_text = "".join([unicode(x) for x in signature])
            if content_text == STRING_MODDED:
                post_status = Post.MODDED
            elif content_text == STRING_CLOSED:
                post_status = Post.CLOSED

            creator = User(username=poster)
            p = Post(topic=self.topic, creator=creator, date=dt,
                    post_num=post_num, contents=content_text,
                    signature=signature_text, status=post_status)

            posts.append(p)
        return posts
