# -*- coding: utf-8 -*-
from urllib import urlencode
import urllib2
import cookielib
from django.conf import settings
from bs4 import BeautifulSoup

class AuthenticationError(StandardError):
    pass

def authenticate(email, password):
    """ logs into gamefaqs using the given (username, password)
        
        Returns a urllib2.opener with the login cookie if successful or raise an
        AuthenticationError if not
    """
    login_url = settings.GFAQS_LOGIN_URL
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

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
