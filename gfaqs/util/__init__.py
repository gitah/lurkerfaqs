# -*- coding: utf-8 -*-
import cookielib
import logging
import traceback
import urllib2
from threading import Lock
from functools import wraps
from datetime import datetime

from django.conf import settings

from util.alert import alert_admin


#--- Logging ---#
if settings.DEBUG:
    logger = logging.getLogger(settings.GFAQS_ARCHIVER_DEBUG_LOGGER)
else:
    logger = logging.getLogger(settings.GFAQS_ARCHIVER_LOGGER)

def log_on_error(fn, explode=False):
    """Decorator that logs the stack trace when an error occurs in the function"""
    @wraps(fn)
    def logged_fn(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception, e:
            error_msg = ["== Error =="]
            error_msg.extend([traceback.format_exc()])
            error_msg.extend(["========", ''])
            error_msg = '\n'.join(error_msg)
            log_error(error_msg, alert=True)
            if explode:
                raise e

    return logged_fn

def log_info(msg):
    logger.info(msg)

def log_debug(msg):
    logger.debug(msg)

def log_error(msg, alert=False):
    if alert and settings.EMAIL_HOST:
        alert_admin("LURKERFAQS APPLICATION ERROR", msg)
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
