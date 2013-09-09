# -*- coding: utf-8 -*-
import cookielib
import logging
import traceback
import urllib2
from threading import Lock
from functools import wraps
from datetime import datetime

from django.conf import settings


#--- Logging ---#
if settings.DEBUG:
    logger = logging.getLogger(settings.GFAQS_ARCHIVER_DEBUG_LOGGER)
else:
    logger = logging.getLogger(settings.GFAQS_ARCHIVER_LOGGER)

def log_on_error(fn, explode=False):
    """Decorator that logs the stack trace when an error occurs in the function"""
    def log_error(e):
        error_msg = ["== Error =="]
        error_msg.extend([traceback.format_exc()])
        error_msg.extend(["========", ''])
        logger.error('\n'.join(error_msg))

    @wraps(fn)
    def logged_fn(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception, e:
            log_error(e)
            if explode:
                raise e

    return logged_fn

def log_info(msg):
    logger.info(msg)

def log_debug(msg):
    logger.debug(msg)

def log_error(msg):
    logger.error(msg)


#--- Threading ---#
strptime_mutex = Lock()
def strptime(date_str, format_str):
    """Thread safe call to datetime.strptime

    See: http://bugs.python.org/issue7980
    """
    strptime_mutex.acquire()
    try:
        return datetime.strptime(date_str, format_str)
    finally:
        strptime_mutex.release()
