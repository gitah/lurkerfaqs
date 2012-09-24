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
    post_data = {
        "EMAILADDR": email,
        "PASSWORD": password,
        "path": settings.GFAQS_URL,
        "key": _get_login_key()
    }
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    # attempt login
    resp = opener.open(login_url, urlencode(post_data))

    if not _validate_login(resp):
        raise AuthenticationError("Invalid password/username")

    return opener

def _get_login_key():
    """ GameFAQs requires a 'key' field when logging in
        This method makes url request to main page and gets the key """
    fp = urllib2.urlopen(settings.GFAQS_URL)
    html = "".join(fp.readlines())
    soup = BeautifulSoup(html)
    soup.find(id="login").find_all("input", name="hidden")
    f.find(attrs={"name": "key"}).get['value']

def _validate_login(resp):
    """ Inspects the response from a login attempt and returns true if login
        successful
    """
    fp = urllib2.urlopen(settings.GFAQS_URL)
    html = "".join(fp.readlines())
    soup = BeautifulSoup(html)

    return bool(soup.find(id="mast_user"))
