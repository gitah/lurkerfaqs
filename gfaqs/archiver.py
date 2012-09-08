import time
from threading import Thread

from scraper import BoardScraper, TopicScraper
from models import Board, Topic

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

"""
TODO:
    - TODO: thread Board/Topic scrapers, threadpools
    - TODO: daemonize
"""
class BoardArchiverThread(Thread):
    def __init__(board, refresh):
        self.board = board
        self.refresh = refresh

    def start():
        Archiver.archive_board(self.board)
        time.sleep(refresh*60)
    
class Archiver():
    """ A daemon that scrapers and saves Boards """
    def __init__(self, board_info=settings.GFAQS_BOARDS,
            base=settings.GFAQS_BASE_URL):

        self.threads = []
        for path,name,refresh in board_info:
            board_url = "%s/%s" % (base,path)
            # create board if not in db
            try:
                board = Board.objects.get(url=board_url)
            except ObjectDoesNotExist:
                board = Board(url=board_url,name=name)
                board.save()

            th = BoardArchiverThread(board,refersh)
            self.threads.add(th)

    def start(self):
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
            t.save()
            if recursive:
                Archiver.archive_post(t)

    @staticmethod
    def archive_topic(t):
        ts = TopicScraper(b)
        for p in ts.retrieve():
            try:
                p_db = Topic.objects.get(gfaqs_id=t.gfaqs_id)
                t.pk = p_db.pk
            except ObjectDoesNotExist:
                t.pk = None
            p.save()
