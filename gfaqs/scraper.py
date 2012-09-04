import urllib
from urlparse import urlparse
from datetime import datetime

from bs4 import BeautifulSoup
from gfaqs.models import User, Board, Topic, Post

#TODO: fill and possibly move somewhere else
TOPIC_STATUS_MAP = {
    "topic.gif": "normal",
    "lock.gif": "locked",
    "topic_poll.gif": "poll",
    "topic_archived.gif": "archived"
}

class Scraper(object):
    def get_page(self, pg):
        #TODO: catch http errors
        base = self.base_url()
        parts = urlparse(base)
        if parts.scheme == "http":
            page_url = "%s?page=%s" % (base,pg)
        elif parts.scheme == "file":
            # for testing purposes
            path = "/".join(parts.path.split("/")[:-1])
            f = parts.path.split("/")[-1]
            name,ext = f.split(".")
            page_url = "%s:///%s/%s-%s.%s" % (parts.scheme,path,name,pg,ext)
        else:
            raise ValueError("URL scheme %s not recognized") % parts.scheme

        return "".join(urllib.urlopen(page_url).readlines())

    def retrieve(self):
        """ generator that returns the next object the scraper will scrape """
        pg = 0
        while True:
            html = self.get_page(pg)
            try:
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
        # TODO: handle exceptions for badly formatted pages
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
            assert topic_status, "Board Parser Error: status image not found"

            topic_gfaqs_id = tds[1].a["href"].split("/")[-1]
            topic_title = tds[1].a.text

            creator = User(username=tds[2].span.text)
            post_count = tds[3].text

            #TODO: convert to datetime obj? ex.8/30 9:00AM
            last_post_date = tds[4].a.text #


            topic = Topic(board=self.board, creator=creator, 
                    gfaqs_id=topic_gfaqs_id, title=topic_title,
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
            raise ValueError("Page contains no topics")

        for tr in post_tags:
            tds = tr.find_all("td")
            if not tds:
                continue
            assert len(tds) == 2, "Board Parser Error: post html invalid format"

            postinfo = list(tds[0].div.children)
            assert len(postinfo) == 8, "Board Parser Error: post html invalid format"
            post_num = postinfo[0]["name"]
            poster = postinfo[1].text

            # Date format:
            format_str = u"%m/%d/%Y %I:%M:%S\\xa0%p"
            #TODO: \xa0 char?
            date_raw = repr(postinfo[3]) 
            #print postinfo[3], str(postinfo[3]), date_raw, date_raw[0]
            dt = datetime.strptime(date_raw,format_str)

            comps = list(tds[1].div.children)
            contents = []
            i = 0
            while i < len(comps):
                comp = comps[i]
                if comp.name == "br" and i+1 < len(comps):
                    if comps[i+1] == "---":
                        break 
                else:
                    contents.append(post_comps[i])
                i += 1

            signature = []
            i += 2
            while i < len(post_comps):
                signature.append(comps[i])

            content_text = "".join([str(x) for x in contents])
            signature_text = "".join([str(x) for x in signature])

            #TODO: edited status
            creator = User(username=poster)
            p = Post(topic=self.topic, creator=creator, date=dt,
                    post_num=post_num, contents=content_text,
                    signature=signature_text, status=0)

            posts.append(p)
