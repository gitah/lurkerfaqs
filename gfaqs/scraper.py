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
    "board_icon_poll": Topic.NORMAL,
    "board_icon_closed": Topic.CLOSED,
    "board_icon_poll": Topic.POLL,
    # TODO: find these
    #"topic_poll_closed.gif": Topic.POLL_CLOSED,
    #"topic_poll_archived.gif": Topic.POLL_ARCHIVED,
    #"topic_archived.gif": Topic.ARCHIVED,
    #"topic_closed.gif": Topic.CLOSED,
    #"sticky.gif": Topic.STICKY,
    #"sticky_closed.gif": Topic.STICKY_CLOSED,
}

STRING_EDITED = "(edited)";
STRING_MODDED = "[This message was deleted at the request of a moderator or administrator]";
STRING_CLOSED = "[This message was deleted at the request of the original poster]";

TOPIC_DATE_FORMAT_STR = "%m/%d %I:%M%p"
TOPIC_DATE_ALT_FORMAT_STR = "%m/%d/%Y"
POST_DATE_FORMAT_STR = "Posted %m/%d/%Y %I:%M:%S %p"

#GFAQS_ENCODING="ISO8559-1"
# <rage>
# The code below took me 3 hours to debug all because all because gfaqs is
# backwards as fuck. Yes I'm mad.
#
# Modern sites basically all use UTF-8 encoding, but no not gfaqs: the header
# and HTML says the page uses ISO-8859-1. This would be alright, but guess
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


class BoardScraper(Scraper):
    def __init__(self, board):
        self.board = board

    def retrieve(self, gfaqs_client):
        pg = 0
        while True:
            try:
                html = gfaqs_client.get_topic_list(self.board, pg)
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

        topic_table = soup.find("table", class_="board topics tlist")
        if not topic_table:
            raise ValueError("Page contains no posts")
        topic_tags = topic_table.find_all("tr")
        topic_tags = topic_tags[1:] # not interested in header line with <th>

        for topic_tag in topic_tags:
            # STATUS IMAGE
            # <td> <i class="board_icon board_icon_topic"></i> <td>
            status_td = topic_tag.find("td", class_="board_status")
            status_classes = status_td.i["class"]
            status_classes.remove("board_icon")
            status_img = status_classes[0]
            topic_status = TOPIC_STATUS_MAP.get(status_img, Topic.NORMAL)
            if status_img not in TOPIC_STATUS_MAP:
                # TODO: log that we need to update status image
                # log "status image %s not found (%s)" % (status_img)
                pass

            # TOPIC NAME
            # <td ><a href="/boards/$BOARD_ALIAS/$TOPIC_ID">$TOPIC_NAME</a></td>
            topic_td = topic_tag.find("td", class_="topic")
            topic_gfaqs_id = topic_td.a["href"].split("/")[-1]
            topic_title = topic_td.a.text

            # AUTHOR
            # <td><span><a class="nobold" # href="...">$USERNAME</a></span></td>
            # we split because username might have (M) at the end
            username_td = topic_tag.find("td", class_="tauthor")
            username = username_td.text.split()
            if "(M)" in username[-1]:
                username = username[:-1]
            username = ' '.join(username)
            creator = User(username=username)

            # POST COUNT
            # <td class="count">1</td>
            post_count_td = topic_tag.find("td", class_="count")
            post_count = int(post_count_td.text)

            # DATE
            # <td class="lastpost"><a href="...">${<M>/<d> <h>:<mm><am/pm>}</a></td>
            try:
                date_td = topic_tag.find("td", class_="lastpost")
                date_raw = date_td.a.text
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
        post_table = soup.find("table", class_="board message msg")
        if not post_table:
            raise ValueError("Page contains no posts")

        post_tags = post_table.find_all("tr")
        for tr in post_tags:
            tds = tr.find_all("td")
            if not tds:
                continue
            assert len(tds) == 2, "post html invalid format (%s)" % self.base_url()

            postinfo = tr.find("td", class_="author")

            """"
            PostInfo HTML Structure:
            0) <span class="author_data">
                    <a name="1"></a>
                    1) <span class="author_data"><a href="/users/Roxas_Oblivion/boards" class="name"><b>Roxas_Oblivion</b></a></span>
                    2) <span class="author_data">Posted 9/3/2013 6:24:13&nbsp;AM</span>
                    3) <span class="author_data"><a href="/boards/2000121-anime-and-manga-other-titles/67150473/756743427">message detail</a></span>
                    4) <span class="author_data"><a href="/boards/post.php?board=2000121&amp;topic=67150473&amp;quote=756743427">quote</a></span>
                    5) <span class="author_data">(edited)</span>
               </span>
            """
            author_data_els = postinfo.find("span", class_="author_data")
            post_num = author_data_els.a["name"]
            for el in author_data_els.findAll("span", class_="author_data"):
                if el.string and el.string.startswith("Posted"):
                    date_raw = el.text
                    # this gets rid of the &nsbp unicode char point (0xA0)
                    date_split = date_raw.split()
                    dt = strptime(" ".join(date_split), POST_DATE_FORMAT_STR)
                elif el.find("a") and el.a["href"].startswith("/users/"):
                    poster = el.a.text

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
            else:
                post_status = Post.NORMAL

            creator = User(username=poster)
            p = Post(topic=self.topic, creator=creator, date=dt,
                    post_num=post_num, contents=content_text,
                    signature=signature_text, status=post_status)

            posts.append(p)
        return posts
