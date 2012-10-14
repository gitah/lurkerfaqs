import urllib2
import logging
from urlparse import urlparse
from datetime import datetime

from bs4 import BeautifulSoup, element
from django.conf import settings

from gfaqs.models import User, Board, Topic, Post

TOPIC_STATUS_MAP = {
    "topic.gif": Topic.NORMAL,
    "lock.gif": Topic.CLOSED,
    "topic_poll.gif": Topic.POLL,
    "topic_archived.gif": Topic.ARCHIVED
}
STRING_EDITED = "(edited)";
STRING_MODDED = "[This message was deleted at the request of a moderator or administrator]";
STRING_CLOSED = "[This message was deleted at the request of the original poster]";

TOPIC_DATE_FORMAT_STR = "%m/%d %I:%M%p"
TOPIC_DATE_ALT_FORMAT_STR = "%m/%d/%Y"
POST_DATE_FORMAT_STR = "Posted %m/%d/%Y %I:%M:%S %p"

logger = logging.getLogger(settings.GFAQS_ERROR_LOGGER)

class Scraper(object):
    def get_page(self, opener, pg):
        base = self.base_url()
        parts = urlparse(base)
        if parts.scheme == "http":
            page_url = "%s?page=%s" % (base,pg)
        else:
            raise ValueError("URL scheme %s not recognized") % parts.scheme

        try:
            return "".join(opener.open(page_url).readlines())
        except IOError:
            raise ValueError("page not found")

    def retrieve(self, opener=None):
        """ generator that returns the next object the scraper will scrape """
        if not None:
            opener=urllib2.build_opener()

        pg = 0
        while True:
            try:
                html = self.get_page(opener,pg)
                for topic in self.parse_page(html):
                    yield topic
                pg += 1
            except ValueError:
                break

    def parse_page(self, html):
        # implement in subclass
        raise NotImplementedError()

    def base_url(self):
        # implement in subclass
        raise NotImplementedError()


class BoardScraper(Scraper):
    def __init__(self, board):
        self.board = board

    def base_url(self):
        """ returns the base url (without page numbers) of the board """
        return self.board.url
    
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
        # TODO: handle exceptions for badly formatted pages; write archiver first
        soup = BeautifulSoup(html)
        topics = []
        topic_tags = soup.find_all("tr")
        if not topic_tags:
            raise ValueError("Page contains no topics")
        for topic_tag in topic_tags:
            tds = topic_tag.find_all("td")
            if not tds:
                continue
            assert len(tds) == 5, "Board Parser Error: topic html invalid format"

            status_img = tds[0].img["src"].split("/")[-1]
            topic_status = TOPIC_STATUS_MAP.get(status_img, None)
            assert topic_status!=None, "Board Parser Error: status image not found"

            topic_gfaqs_id = tds[1].a["href"].split("/")[-1]
            topic_title = tds[1].a.text

            creator = User(username=tds[2].span.text)
            post_count = int(tds[3].text)

            try:
                date_raw = tds[4].a.text
                dt = datetime.strptime(date_raw,TOPIC_DATE_FORMAT_STR)
                # the year is not sepcified on gfaqs, 
                # so I'll set it to the current year
                curr_year = datetime.now().year
                dt = datetime(curr_year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            except ValueError:
                # archived topic, use alternative format str
                dt = datetime.strptime(date_raw,TOPIC_DATE_ALT_FORMAT_STR)

            topic = Topic(board=self.board, creator=creator, 
                    gfaqs_id=topic_gfaqs_id, title=topic_title,
                    number_of_posts=post_count, last_post_date=dt, 
                    status=topic_status)
            topics.append(topic)

        return topics

class TopicScraper(Scraper):
    def __init__(self, topic):
        self.topic = topic

    def base_url(self):
        """ returns the base url (without page numbers) of the topic """
        board_url = self.topic.board.url
        return "%s/%s" % (board_url, self.topic.gfaqs_id)

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
        soup = BeautifulSoup(html)
        posts = []
        post_tags = soup.find_all("tr")
        if not post_tags:
            raise ValueError("Page contains no posts")

        for tr in post_tags:
            tds = tr.find_all("td")
            if not tds:
                continue
            assert len(tds) == 2, "Board Parser Error: post html invalid format"

            postinfo = list(tds[0].div.children)
            post_status = Post.NORMAL
            for el in postinfo:
                if type(el) == element.NavigableString:
                    if el.string.startswith("Posted"):
                        date_raw = " ".join(el.string.split())
                        #TODO: set year on dt obj
                        dt = datetime.strptime(date_raw,POST_DATE_FORMAT_STR)
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
                if hasattr(comp,"name") and comp.name == "br" and i+1 < len(comps):
                    if comps[i+1] == "---":
                        break 
                else:
                    contents.append(comp)
                i += 1

            signature = []
            i += 2
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
