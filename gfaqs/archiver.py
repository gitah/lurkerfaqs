import time
from threading import Thread

from daemon import Daemon
from scraper import BoardScraper, TopicScraper
from models import User, Board, Topic, Post

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

#TODO: thread Board/Topic scrapers, threadpools
class BoardArchiverThread(Thread):
    def __init__(self, board, refresh):
        self.board = board
        self.refresh = refresh
        self.sleeping = False

    def start(self):
        while True:
            Archiver.archive_board(self.board)
            self.sleeping = True
            time.sleep(self.refresh*60)
            self.sleeping = False
    
class Archiver(Daemon):
    """ A daemon that scrapers and saves Boards """
    def __init__(self, board_info=settings.GFAQS_BOARDS,
            base=settings.GFAQS_BASE_URL,
            pidfile=settings.GFAQS_ARCHIVER_PID_FILE):
        self.board_info = board_info
        self.base_url = base
        self.threads = []
        super(Archiver,self).__init__(pidfile)

    def run(self):
        for path,name,refresh in self.board_info:
            board_url = "%s/%s" % (self.base_url,path)
            # create board if not in db
            try:
                board = Board.objects.get(url=board_url)
            except ObjectDoesNotExist:
                board = Board(url=board_url,name=name)
                board.save()
                print board.url, board.name

            th = BoardArchiverThread(board,refresh)
            self.threads.append(th)

        print len([th.board for th in self.threads])
        """ Starts the archiver """
        for th in self.threads:
            th.start()

    @staticmethod
    def archive_board(b, recursive=True):
        """ scrapes and saves the topics of a board to the db 
        
            b: the models.Board to archive
            recursive: archives the posts of each topic as well
        """
        bs = BoardScraper(b)
        #TODO: make one query for all topics
        for t in bs.retrieve():
            try:
                t_db = Topic.objects.get(gfaqs_id=t.gfaqs_id)
                t.pk = t_db.pk
                if t_db.number_of_posts == t.number_of_posts:
                    # this is the first topic that hasn't been updated 
                    # since last archive run, so we stop
                    break 
            except ObjectDoesNotExist:
                t.pk = None
            t.creator = Archiver.add_user(t.creator)
            t.save()
            if recursive:
                Archiver.archive_topic(t)

    @staticmethod
    def archive_topic(t):
        """
        TODO: 
        handle exceptions
            - t not in db
            - multiple results errors for *.get() calls
        """
        ts = TopicScraper(t)
        for p in ts.retrieve():
            # Check of post exists already in db to determine update or add
            try:
                p_db = Post.objects.filter(topic_id=t.id).get(
                    post_num=p.post_num)
                # TODO: update instead of ignore, revisions ???
                continue
            except ObjectDoesNotExist:
                p.pk = None
            p.creator = Archiver.add_user(p.creator)
            p.save()

    @staticmethod
    def add_user(user):
        """ Check if user exists already in db, if not add it """
        if user.id:
            return user
        try:
            return User.objects.get(username=user.username)
        except ObjectDoesNotExist:
            user.save()
        return user
