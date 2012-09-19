from urllib import urlencode
import urllib2
from django.config import settings

class AuthenticationError(StandardError):
    pass

def login(email, password):
    """ logs into gamefaqs using the given (username, password)
        
        Returns a cookie if successful or raise an AuthenticationError if not
    """
    login_url = settings.GFAQS_LOGIN_URL
    post_data = {
        "EMAILADDR": email,
        "PASSWORD": password,
        "path": settings.GFAQS_BASE_URL,
        "key": _get_login_key()
    }
    resp = urllib2.urlopen(login_url, urlencode(post_data))
    cookie = _get_cookie(resp)

    if not cookie:
        raise AuthenticationError("Invalid password/username")
    return cookie

def _get_login_key():
    """ GameFAQs requires a 'key' field when logging in
        This method makes url request to main page and gets the key """
    pass

def _get_cookie(resp):
    """ Inspects the response from a login attempt gets the cookie
        returns None if no cookie is found
    """
    headers = dict(resp.info())
    return headers.get("Set-Cookie")
