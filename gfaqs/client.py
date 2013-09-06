# -*- coding: utf-8 -*-
"""
An accessor class for Gamefaqs

Currently it is implemented using python's urlib2
"""
import urllib2
import cookielib
from urllib import urlencode

from django.conf import settings
from bs4 import BeautifulSoup

from gfaqs.util import log_on_error, log_info
from gfaqs.models import User, Board, Topic, Post

class GFAQSClient(object):
    def __init__(self, email=None, password=None):
        log_info("Creating urllib2 connection")
        if email and password:
            self.opener = authenticate(settings.GFAQS_LOGIN_EMAIL, settings.GFAQS_LOGIN_PASSWORD)
            log_info("Logged in as %s" % settings.GFAQS_LOGIN_EMAIL)
        else:
            self.opener = build_opener()
            log_info("No login specified")

    def _generate_query_string(self, page):
        """Returns a query string for a URL to a board or topic"""
        query = {
            "page": page,
            "results": 1,  #display poll results
        }
        return urlencode(query)

    def get_topic_list(self, board, pg):
        """Fetches the given topic list page"""
        base = board.url
        qs = self._generate_query_string(pg)
        page_url = "%s?%s" % (base, qs)
        try:
            return "".join(self.opener.open(page_url).readlines())
        except IOError:
            raise ValueError("page not found")

    def get_post_list(self, topic, pg):
        """Fetches the given topic list page"""
        board_url = topic.board.url
        base = "%s/%s" % (board_url, topic.gfaqs_id)
        qs = self._generate_query_string(pg)
        page_url = "%s?%s" % (base, qs)
        try:
            return "".join(self.opener.open(page_url).readlines())
        except IOError:
            raise ValueError("page not found")


#--- Login ---#
class AuthenticationError(StandardError):
    pass

def authenticate(email, password):
    """ logs into gamefaqs using the given (username, password)
        
        Returns a urllib2.opener with the login cookie if successful or raise an
        AuthenticationError if not
    """
    login_url = settings.GFAQS_LOGIN_URL

    opener = build_opener()
    cj = cookielib.CookieJar()
    opener.add_handler(urllib2.HTTPCookieProcessor(cj))
    foo = opener.open('http://www.gamefaqs.com')

    post_data = {
        "EMAILADDR": email,
        "PASSWORD": password,
        "path": settings.GFAQS_URL,
        "key": _get_login_key(opener)
    }

    # attempt login
    resp = opener.open(login_url, urlencode(post_data))
    _validate_login(cj)
    return opener

def _get_login_key(opener):
    """ GameFAQs requires a 'key' field when logging in
        This method makes url request to main page and gets the key """
    fp = opener.open(settings.GFAQS_URL)
    html = "".join(fp.readlines())
    soup = BeautifulSoup(html)
    login_tag = soup.find(id="login")
    return login_tag.find_all("input")[1]['value']

def _validate_login(cj):
    """ Inspects the response from a login attempt and returns true if login
        successful
    """
    try:
        cj._cookies['.gamefaqs.com']['/']['MDAAuth']
    except KeyError:
        raise AuthenticationError("Invalid password/username")

#--- Connection ---#
def build_opener():
    """a factory to create an appropriate urllib2 opener object"""
    handlers = []
    if settings.HTTP_PROXY:
        proxy_info = {"http": settings.HTTP_PROXY}
        handlers.append(urllib2.ProxyHandler(proxy_info))
    opener = urllib2.build_opener(*handlers)
    if settings.UA_HEADER:
        opener.addheaders = [('User-agent', settings.UA_HEADER)]
    return opener
