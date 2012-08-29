import urllib
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup
from gfaqs.models import Board, Topic, Post

class Scraper(object):
    def get_page(self, pg):
        #TODO: format properly, catch http errors
        parts = urlparse(self.baseurl)
        if parts.scheme == "http":
            page_url = "%s?page=%s" % (self.base_url,pg)
        elif parts.scheme = "file":
            # for testing purposes
            page_url = "%s-s" % (self.base_url,pg)
        else:
            raise ValueError("URL scheme %s not recognized" % parts.scheme

        return "".join(urllib.urlopen(page_url).readlines())

    def retrieve(self):
        """ generator that returns the next object the scraper will scrape """
        pg = 0
        while True:
            doc = self.get_page(pg)
            try:
                for topic in self.parse_page(doc):
                    yield topic
                pg += 1
            except ValueError:
                break

    def parse_page(self, doc):
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
    
    def parse_page(self, doc):
        """ parses the page and returns a list of Topic objects """
        # TODO
        #   Exception: throws ValueError when page doesn't exist
        soup = BeautifulSoup(doc)

class TopicScraper(Scraper):
    def __init__(self, topic):
        self.topic = topic

    def base_url(self):
        """ returns the base url (without page numbers) of the topic """
        #TODO: format properly
        board_url = self.topic.board.url
        return "%s?id=%s" % (board_url, self.topic.gfaqs_id)

    def parse_page(self, doc):
        """ parses the page and returns a list of Post objects """
        # TODO
        pass
