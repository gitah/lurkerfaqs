import urllib
from urlparse import urlparse

from bs4 import BeautifulSoup
from gfaqs.models import Board, Topic, Post

#TODO: fill and possibly move somewhere else
TOPIC_STATUS_MAP = {
    "topic.gif": "normal",
    "lock.gif": "locked"
}

class Scraper(object):
    def get_page(self, pg):
        #TODO: format properly, catch http errors
        parts = urlparse(self.baseurl)
        if parts.scheme == "http":
            page_url = "%s?page=%s" % (self.base_url,pg)
        elif parts.scheme = "file":
            # for testing purposes
            page_url = "%s-s.html" % (self.base_url,pg)
        else:
            raise ValueError("URL scheme %s not recognized" % parts.scheme

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
            sec = topic_tag.find_all("td")
            if not sec:
                continue
            assert len(sec) == 4, "Board Parser Error: topic html invalid format"

            status_img = sec[0].img["src"].split("/")[-1]
            topic_status = TOPIC_STATUS_MAP.get(status_img, None)
            assert topic_status, "Board Parser Error: status image not found"

            topic_gfaqs_id = sec[1].a["href"].split("/")[-1]
            topic_title = sec[1].a.text

            creator = User(username=sec[2].span.text)
            post_count = sec[3].text
            last_post_date = sec[4].a.text #TODO: convert to datetime obj?

            topic = Topic(board=self.board, creator=creator, 
                    gfaqs_id=topic_gfaqs_id, title=topic_title
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

        for post_tag in post_tags:
            sec = topic_tag.find_all("td")
            if not sec:
                continue
            assert len(sec) == 2, "Board Parser Error: post html invalid format"

            #TODO: parse post date
            ps_tag = sec[0].find_all("a")
            assert len(ps_tag) == 3, "Board Parser Error: post html invalid format"
            post_count = ps_tag[0]["name"]
            user_count = ps_tag[1].text

            comps = list(sec[1].div.children)
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
