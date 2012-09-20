import time
import urllib2
from threading import Thread

from utils.daemon import Daemon
from utils.threadpool import ThreadPool
from scraper import BoardScraper, TopicScraper
from models import User, Board, Topic, Post
from login import authenticate

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

#TODO: transactions
WORKERS_PER_BOARD = 10

class Archiver(Daemon):
    """ A daemon that scrapers and saves Boards """
    def __init__(self, board_info=settings.GFAQS_BOARDS,
            base=settings.GFAQS_BASE_URL,
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

        for path,name,refresh in self.board_info:
            board_url = "%s/%s" % (self.base_url,path)
            # create board if not in db
            try:
                board = Board.objects.get(url=board_url)
            except ObjectDoesNotExist:
                board = Board(url=board_url,name=name)
                board.save()
            self.pool.add_task(archive_board_task, board, refresh)

    def archive_board(self, b, recursive=True):
        """ scrapes and saves the topics of a board to the db 
        
            b: the models.Board to archive
            recursive: archives the posts of each topic as well
        """
        bs = BoardScraper(b)

        for t in bs.retrieve(self.opener):
            try:
                t_db = Topic.objects.get(gfaqs_id=t.gfaqs_id)
                t.pk = t_db.pk
                if t_db.number_of_posts == t.number_of_posts:
                    # this is the first topic that hasn't been updated 
                    # since last archive run, so we stop
                    break 
            except ObjectDoesNotExist:
                t.pk = None
            t.creator = self.add_user(t.creator)
            t.save()
            if recursive:
                self.pool.add_task(self.archive_topic,t)

    def archive_topic(self, t):
        """
        TODO:
        handle exceptions
            - t not in db
            - multiple results errors for *.get() calls
        """
        ts = TopicScraper(t)

        for p in ts.retrieve(self.opener):
            # Check of post exists already in db to determine update or add
            try:
                p_db = Post.objects.filter(topic_id=t.id).get(
                    post_num=p.post_num)
                # TODO: update instead of ignore, revisions ???
                continue
            except ObjectDoesNotExist:
                p.pk = None
            p.creator = self.add_user(p.creator)
            p.save()

    def add_user(self, user):
        """ Check if user exists already in db, if not add it """
        if user.id:
            return user
        try:
            return User.objects.get(username=user.username)
        except ObjectDoesNotExist:
            user.save()
        return user
