# -*- coding: utf-8 -*-
import time
from threading import Thread
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import connection, transaction

from gfaqs.util import log_on_error, log_info, log_debug, log_error
from gfaqs.util.daemon import Daemon
from gfaqs.util.threadpool import ThreadPool
from gfaqs.scraper import BoardScraper, TopicScraper
from gfaqs.models import User, Board, Topic, Post
from gfaqs.client import GFAQSClient


WORKERS_PER_BOARD = 10      # number of worker thread created for each board
THROTTLE_TIME = 0.1         # time in secs between performing gfaqs IO operations
BOARD_STAGGER_TIME = 30     # time in secs between starting each board scraper

def throttle_thread(throttle_time=THROTTLE_TIME):
    """Halts one of the archiver thread for a bit, to not overwhelm gamefaqs"""
    time.sleep(throttle_time)

class Archiver(Daemon):
    """ A daemon that scrapers and saves Boards """
    def __init__(self, board_info=settings.GFAQS_BOARDS,
            base=settings.GFAQS_BOARD_URL,
            pidfile=settings.GFAQS_ARCHIVER_PID_FILE):
        super(Archiver,self).__init__(pidfile)
        self.board_info = board_info
        self.base_url = base
        self.gfaqs_client = GFAQSClient()

    def run(self):
        # Build GFAQSClient to access webpage
        if settings.GFAQS_LOGIN_AS_USER:
            self.gfaqs_client = GFAQSClient(settings.GFAQS_LOGIN_EMAIL, settings.GFAQS_LOGIN_PASSWORD)

        # Initialize threadpool
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
                # we want boards to start at different times to spread out load
                time.sleep(BOARD_STAGGER_TIME)

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
        log_info("Archiving Board (%s) started" % b.alias)
        topics_examined, topics_saved = 0, 0

        try:
            for t in bs.retrieve(self.gfaqs_client):
                topics_examined += 1
                if t.status in Topic.ARCHIVED_STATUSES:
                    # we reached archived topics; don't continue
                    break
                try:
                    t_db = Topic.objects.get(gfaqs_id=t.gfaqs_id)
                    t.pk = t_db.pk
                    if t_db.number_of_posts == t.number_of_posts:
                        if t.status in Topic.STICKY_STATUSES:
                            continue
                        else:
                            # this is the first topic that hasn't been updated since
                            # last archive run, so we stop
                            break
                except ObjectDoesNotExist:
                    t.pk = None

                with transaction.commit_on_success():
                    t.creator = self.add_user(t.creator)
                    t.save()
                    topics_saved += 1

                if recursive:
                    self.pool.add_task(self.archive_topic, t)
                throttle_thread()
        except Exception, e:
            log_error("Failed to parse board %s" % b)
            raise e

        log_info("Archiving Board (%s) finished; %s topics examined, %s new" % \
                (b.alias, topics_examined, topics_saved))

    @log_on_error
    def archive_topic(self, t):
        """Scrapes the given topic and saves its posts"""
        ts = TopicScraper(t)
        log_debug("Archiving Topic (%s) started" % t.gfaqs_id)
        posts_examined, posts_saved = 0, 0

        try:
            posts = list(ts.retrieve(self.gfaqs_client))
        except Exception, e:
            log_error("Failed to parse topic %s %" % t)
            raise e

        for p in reversed(posts):
            posts_examined += 1
            # Check if post exists already in db to determine update or add
            with transaction.commit_on_success():
                try:
                    p_db = Post.objects.filter(topic=t).get(post_num=p.post_num)
                    # we already have the rest of the posts in the db
                    break
                except ObjectDoesNotExist:
                    p.creator = self.add_user(p.creator)
                    p.save()
                    posts_saved += 1
                    log_debug("Added Post %s" % t)
            throttle_thread()

        # update poll results if applicable
        if posts and t.status in Topic.POLL_STATUSES:
            p = posts[0]
            p_db = Post.objects.filter(topic=t).get(post_num=p.post_num)
            p_db.contents = p.contents
            p_db.save()
            log_debug("Updated Post %s for poll" % p)

        log_debug("Archiving Topic (%s) finished; %s posts examined, %s new" % (t.gfaqs_id, posts_examined, posts_saved))

    def add_user(self, user):
        """ Check if user exists already in db, if not add it """
        if user.id:
            return user
        try:
            return User.objects.get(username=user.username)
        except ObjectDoesNotExist:
            user.save()
            log_debug("User added (%s)" % user.username)
            return user
