# -*- coding: utf-8 -*-
"""
Methods to turns text urls into anchor links.

This is trickier than it first looks:
http://www.codinghorror.com/blog/2008/10/the-problem-with-urls.html

This implementation is just using the naive approach for now.
"""
import re

HTML_RE = re.compile(r'\b(https?://|www.)[^\s<>]+|[^\s<>]+\.(com|ca|net|org)(/[^\s<>]+)?\b', re.IGNORECASE)
IMAGE_EXT_RE = re.compile(r'(jpg|png|gif)$', re.IGNORECASE)
YOUTUBE_VID_RE = re.compile(r'v=([^\s]{11})', re.IGNORECASE)
YOUTU_VID_RE = re.compile(r'youtu.be/([^\s]{11})',  re.IGNORECASE)

YOUTUBE_HTML = '<iframe id="ytplayer" type="text/html" width="640" height="390" src="http://www.youtube.com/embed/%s?autoplay=0" frameborder="0"></iframe>'
IMAGE_HTML = '<img src="%s" alt="external image"/>'
ANCHOR_HTML = '<a href="%s">%s</a>'

def linkify(text):
    """Adds anchor and image tags to the urls in text"""
    def convert(matchobj):
        url = matchobj.group(0)
        if "youtube.com" in url or "youtu.be" in url:
            try:
                youtube_vid = extract_youtube_vid(url)
                return YOUTUBE_HTML % youtube_vid
            except:
                pass

        if re.search(IMAGE_EXT_RE, url):
            return IMAGE_HTML % url
        else:
            return ANCHOR_HTML % (url, url)

    return re.sub(HTML_RE, convert, text)

def extract_youtube_vid(url):
    if "youtube.com" in url:
        matchobj = re.search(YOUTUBE_VID_RE, url)
        return matchobj.group(1)
    elif "youtu.be" in url:
        matchobj = re.search(YOUTU_VID_RE, url)
        return matchobj.group(1)
