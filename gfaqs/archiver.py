import time
import urllib2
import logging
import traceback
from threading import Thread
from datetime import datetime
from functools import wraps

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import connection, transaction

from utils.daemon import Daemon
from utils.threadpool import ThreadPool
from scraper import BoardScraper, TopicScraper
from models import User, Board, Topic, Post
from login import authenticate


#TODO: transactions
WORKERS_PER_BOARD = 10

#TODO: move Logging stuff to seperate module
err_logger = logging.getLogger(settings.GFAQS_ERROR_LOGGER)
info_logger = logging.getLogger(settings.GFAQS_INFO_LOGGER)

def log_on_error(fn, explode=False):
    """Decorator that logs the stack trace when an error occurs in the function"""
    def log_error(e):
        error_msg = ["== Error =="]
        error_msg.extend([traceback.format_exc()])
        error_msg.extend(["========", ''])
        err_logger.error('\n'.join(error_msg))
        if explode:
            raise e

    @wraps(fn)
    def logged_fn(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception, e:
            log_error(e)

    return logged_fn

def log_info(msg):
    info_logger.info(msg)

class Archiver(Daemon):
    """ A daemon that scrapers and saves Boards """
    def __init__(self, board_info=settings.GFAQS_BOARDS,
            base=settings.GFAQS_BOARD_URL,
            pidfile=settings.GFAQS_ARCHIVER_PID_FILE):
        super(Archiver,self).__init__(pidfile)
        self.board_info = board_info
        self.base_url = base

        # login to gamefaqs
        if settings.GFAQS_LOGIN_AS_USER:
            self.opener = authenticate(settings.GFAQS_LOGIN_EMAIL, settings.GFAQS_LOGIN_PASSWORD)
        else:
            self.opener = urllib2.build_opener()

    def run(self):
        # we need at least one thread for each board
        num_workers = len(self.board_info)* WORKERS_PER_BOARD + 1
        self.pool = ThreadPool(num_workers)
        def archive_board_task(board, refresh):
            while True:
                self.archive_board(board)
                time.sleep(refresh*60)

        for alias,name,refresh in self.board_info:
            board_url = "%s/%s" % (self.base_url, alias)
            # create board if not in db
            with transaction.commit_on_success():
                try:
                    board = Board.objects.get(url=board_url)
                except ObjectDoesNotExist:
                    board = Board(url=board_url, name=name, alias=alias)
                    board.save()
                self.pool.add_task(archive_board_task, board, refresh)

        # hang thread, so daemon keeps running
        while True:
            time.sleep(10)

    @log_on_error
    def archive_board(self, b, recursive=True):
        """ scrapes and saves the topics of a board to the db 
        
            b: the models.Board to archive
            recursive: archives the posts of each topic as well
        """
        bs = BoardScraper(b)
        log_info("Archiving Board (%s) started" % b.url)
        topics_examined, topics_saved = 0, 0

        for t in bs.retrieve(self.opener):
            topics_examined += 1
            try:
                t_db = Topic.objects.get(gfaqs_id=t.gfaqs_id)
                t.pk = t_db.pk
                if t_db.number_of_posts == t.number_of_posts:
                    # this is the first topic that hasn't been updated 
                    # since last archive run, so we stop
                    break 
            except ObjectDoesNotExist:
                t.pk = None

            with transaction.commit_on_success():
                t.creator = self.add_user(t.creator)
                t.save()
                topics_saved += 1

            if recursive:
                self.pool.add_task(self.archive_topic,t)

        log_info("Archiving Board (%s) finished; %s topics examined, %s new" % \
                (b.url, topics_examined, topics_saved))

    @log_on_error
    def archive_topic(self, t):
        """
        TODO:
        handle exceptions
            - t not in db
            - multiple results errors for *.get() calls
        """
        ts = TopicScraper(t)
        log_info("Archiving Topic (%s) started" % t.gfaqs_id)
        posts_examined, posts_saved = 0, 0

        for p in ts.retrieve(self.opener):
            posts_examined += 1
            # Check of post exists already in db to determine update or add
            with transaction.commit_on_success():
                try:
                    Post.objects.filter(topic=t).get(post_num=p.post_num)
                    # TODO: update post instead of ignore for edited ones
                    # TODO: or simply skip until newest topic so less db queries needed
                    continue
                except ObjectDoesNotExist:
                    p.pk = None
                    p.creator = self.add_user(p.creator)
                    p.save()
                    posts_saved += 1

        log_info("Archiving Topic (%s) finished; %s posts examined, %s new" % \
            (t.gfaqs_id, posts_examined, posts_saved))

    def add_user(self, user):
        """ Check if user exists already in db, if not add it """
        if user.id:
            return user
        try:
            return User.objects.get(username=user.username)
        except ObjectDoesNotExist:
            user.save()
            log_info("User added (%s)" % user.username)
            return user
