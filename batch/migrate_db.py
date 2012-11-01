# -*- coding: utf-8 -*-
import traceback

from MySQLdb import connect
from django.db import connection, transaction

from gfaqs.models import Board, User, Topic, Post
from batch.batch_base import Batch

"""
Schema:

boards:
     board_id            int(11)
     url                varchar(100)
     name	            varchar(200)
     next_update	    datetime
     last_topic_date	datetime
     scrape_period	    int(11)

posts:
    post_id	int(11)
	topic_id	int(11)
	user_id	int(11)
	date	datetime
	num	smallint(6)
	contents	text
	signature	text
	status


topics:
    topic_id	int(11)
	board_id	int(11)
	user_id	int(11)
	num	varchar(15)
	title	varchar(100)
	post_count	smallint(5)
	last_post_date	datetime
	status	tinyint(3)


users:
    user_id	int(11)
	username varchar(25)
	status	tinyint(3)
"""

TARGET_DB='lurkerfaqs_test'
CHUNK_SIZE=10000

class MigrateDB(Batch):
    """ Migrates data from the old lurkerfaqs database (different schema) to the
    current one"""
    def __init__(self, host='', port=3306, user='', password='', db=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    def start(self):
        self.conn = connect(host=self.host, port=self.port,
            user=self.user, passwd=self.password, db=self.db)
        # order is important here
        #self.migrate_boards()
        #self.migrate_users()
        #self.migrate_topics()
        self.migrate_posts()

    def migrate_boards(self):
        ForEachBoard().start(self.conn)

    def migrate_users(self):
        ForEachUser().start(self.conn)

    def migrate_topics(self):
        ForEachTopic().start(self.conn)

    def migrate_posts(self):
        ForEachPost().start(self.conn)


class ForEach(object):

    def get_chunk_generator(self, sql_query, total):
        """returns a generator that chunks the sql query using LIMIT 

        ex. sql_query = "select * from boards" 
                1 => "select * from boards limit 0,CHUNK_SIZE"
                2 => "select * from boards limit CHUNK_SIZE, 2*CHUNK_SIZE"
                ...
        """
        def chunk_generator():
            start = 0
            while True:
                limit = "LIMIT %s, %s" % (start, CHUNK_SIZE)
                yield (start, "%s %s" % (sql_query, limit))
                start += CHUNK_SIZE
                if start > total:
                    break
        return chunk_generator

    def print_progress(self, curr, total):
        ratio = float(curr)/float(total)
        print "[%.2f] (%d / %d) rows processed"  % (ratio, curr, total)

    def start(self, conn):
        self.conn = conn

        total = self.get_row_count()

        if self.where_clause():
            sql_query_base = "%s %s" % (self.sql_query(), self.where_clause)
        else:
            sql_query_base = self.sql_query()

        chunk_generator = self.get_chunk_generator(sql_query_base, total)
        for start_index,query in chunk_generator():
            self.print_progress(start_index, total)
            self.visit_chunk(query)
        self.print_progress(total, total)

    def visit_chunk(self, sql):
        c = self.conn.cursor()
        c.execute(sql)

        db_models = []
        for r in c.fetchall():
            try:
                model = self.visit_row(r)
                db_models.append(model)
            except Exception, e:
                traceback.print_exc()

        with transaction.commit_on_success():
            self.table_class.objects.using(TARGET_DB).bulk_create(db_models)

    def get_row_count(self):
        c = self.conn.cursor()
        c.execute(self.row_count_query())
        count, = c.fetchone()
        return int(count)

    def sql_query(self):
        assert self.table_name
        return "SELECT * FROM %s" % self.table_name

    def row_count_query(self):
        assert self.table_name
        return "SELECT COUNT(*) FROM %s" % self.table_name

    def where_clause(self):
        """override this"""
        return ''
    
    def visit_row(self, r):
        """override this"""
        pass

class ForEachBoard(ForEach):

    table_name = "boards"
    table_class = Board

    def visit_row(self, r):
        board_id, url, name, _, _, _ = r
        alias = url.split("http://www.gamefaqs.com/boards/")[1]
        return Board(pk=board_id, url=url, name=name, alias=alias)

class ForEachUser(ForEach):

    table_name = "users"
    table_class = User

    def visit_row(self, r):
        user_id, username, status = r
        return User(pk=user_id, username=username, status=status)

class ForEachTopic(ForEach):

    table_name = "topics"
    table_class = Topic

    def visit_row(self, r):
        topic_id, board_id, user_id, num, title, post_count, last_post_date, status = r
        return Topic(pk=topic_id, board_id=board_id, creator_id=user_id, gfaqs_id=num,
            number_of_posts=post_count, last_post_date=last_post_date, status=status)

class ForEachPost(ForEach):

    table_name = "posts"
    table_class = Post

    def visit_row(self, r):
        post_id, topic_id, user_id, date, num, contents, signature, status = r
        return Post(pk=post_id, topic_id=topic_id, creator_id=user_id, date=date,
            post_num=num, contents=contents, signature=signature, status=status)
