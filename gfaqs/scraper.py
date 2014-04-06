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
        """ topic should be a gfaqs.models.Topic object """
        self.topic = topic

    def retrieve(self, gfaqs_client):
        pg = 0
        while True:
            try:
                html = gfaqs_client.get_post_list(self.topic, pg)
                for topic in self._parse_page(html):
                    yield topic
                pg += 1
            except ValueError:
                break

    def _parse_page(self, html):
        """ parses the page and returns a list of Post objects

            DOM Layout of a topic
            <table class="board messages msg">
                <tr class="msg left"></tr>
                ....
            </table>
        """
        soup = BeautifulSoup(html, from_encoding=GFAQS_ENCODING)
        posts = []
        post_table = soup.find("table", class_="board message msg")
        if not post_table:
            raise ValueError("Page contains no posts")
        post_trs = post_table.find_all("tr")
        for tr in post_trs:
            p = self._parse_post(tr)
            posts.append(p)
        return posts

    def _parse_post(self, post_tr):
        """ post_tr DOM

            <tr class="msg left">
               <td class="author">...</td>
               <td class="msg">.. </tr>
            <tr>
        """
        # Parse post info (username, post date, etc.)
        post_info_td = post_tr.find("td", class_="author")
        (post_num, post_creator, post_dt) = self._parse_post_info(post_info_td)

        # Parse post content
        post_content_td = post_tr.find("td", class_="msg")
        (content_text, signature_text) = self._parse_post_contents(post_content_td)

        post_status = Post.NORMAL
        if content_text == STRING_MODDED:
            post_status = Post.MODDED
        elif content_text == STRING_CLOSED:
            post_status = Post.CLOSED

        creator = User(username=post_creator)
        return Post(topic=self.topic,
                creator=creator,
                date=post_dt,
                post_num=post_num,
                contents=content_text,
                signature=signature_text,
                status=post_status)

    def _parse_post_info(self, post_info_td):
        """ post_info_td DOM

       <td class="author">
        <div class="msg_stats_left">
            <span class="author_data"><a name="1"></a>#1</span>
            <span class="author_data">
                <a href="/users/jumi/boards" class="name">
                    <b>jumi</b>
                </a>
            </span>
            <span class="author_data">Posted 4/5/2014 1:56:08 PM</span>
            <span class="author_data">
                <a href="/boards/2000121-anime-and-manga-other-titles/68960382/779732076">message detail</a>
            </span>
        </div>
       </td>
        """
        post_infos = post_info_td.find_all("span", class_="author_data")
        post_num = post_infos[0].a["name"]
        post_creator = post_infos[1].text
        dt_raw = " ".join(post_infos[2].text.split())
        post_dt = strptime(dt_raw, POST_DATE_FORMAT_STR)
        return (post_num, post_creator, post_dt)

    def _parse_post_contents(self, post_content_td):
        """ post_content_td DOM

           <td class="msg">
               <div class="msg_body">
                    <div class="message_mpu">...</div>
                    post contents
                    <br>
                    ---
                    <br>
                    Signature
               </div>
           </td>
        """
        msg_body_div = post_content_td.find("div", class_="msg_body")
        # remove the post ads
        post_ad_div = msg_body_div.find("div", class_="message_mpu")
        if post_ad_div is not None:
            post_ad_div.extract()

        # extract post content
        contents = []
        comps = list(msg_body_div.children)
        i = 0
        while i < len(comps):
            comp = comps[i]
            # parse until we reach signature
            if hasattr(comp, "name") and comp.name == "br" and i+2 < len(comps):
                if comps[i+1] == "---":
                    break
            contents.append(comp)
            i += 1

        # extract post signature
        signature = []
        i += 3
        while i < len(comps):
            signature.append(comps[i])
            i += 1

        content_text = "".join([unicode(x) for x in contents])
        signature_text = "".join([unicode(x) for x in signature])
        return (content_text, signature_text)

