import argparse

from MySQLdb import connect

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


class MigrateDB(Batch):
    """ Migrates data from the old lurkerfaqs database (different schema) to the
    current one"""
    def __init__(self):
        parser = argparse.ArgumentParser(description='migrates old lurkerfaqs db')
        parser.add_argument('host', type=str, nargs='1',
           help='hostname of mysql db to migrate')
        parser.add_argument('--user', dest=user, type=str, nargs='1',
           help='username of mysql db')
        parser.add_argument('--password', dest=password, type=str, nargs='1',
           help='password of mysql db')

        args = parser.parse_args()
        self.src_db_host = args.host
        self.src_db_port = args.port
        self.db_user = args.user
        self.db_password = args.password

    def start(self):
        # parse args
        self.conn = connect(host=self.host, user=self.db_user, passwd=self.db_password)

    def migrate_boards(self):
        ForEachBoard().start(self.conn)

    def migrate_users(self):
        ForEachUser().start(self.conn)

    def migrate_topics(self):
        ForEachTopic().start(self.conn)

    def migrate_posts(self):
        ForEachPost().start(self.conn)


class ForEach(object):
    def get_chunk_generator(self, sql_query):
        """returns a generator that chunks the sql query using LIMIT 

        ex. sql_query = "select * from boards" 
                1 => "select * from boards limit 0,CHUNK_SIZE"
                2 => "select * from boards limit CHUNK_SIZE, 2*CHUNK_SIZE"
                ...
        """
        CHUNK_SIZE=100
        def chunk_generator():
            start = 0
            while True:
                limit = "LIMIT %s, %s" % (start, start+CHUNK_SIZE)
                yield "%s %s" % (sql_query, limit)
                start += CHUNK_SIZE

        return chunk_generator

    def start(self, conn):
        self.conn = conn
        chunk_generator = get_chunk_generator(self.get_sql_query())
        for sql in chunk_generator():
            #TODO: catch exception for bad query and break
            visit_chunk(sql)

    def visit_chunk(self, sql):
        c = self.conn.cursor()
        c.execute(sql)
        with transaction.commit_on_success():
            for r in c.fetchone()
                #TODO: handle exception with row?
                self.visit_row(r)

    def get_sql_query(self):
        """override this"""
        pass
    
    def visit_row(self):
        """override this"""
        pass

class ForEachBoard(ForEach):

    def visit_row(r):
        board_id, url, name, _, _, _ = r
        #TODO: parse alias from board url
        b = Board(pk=board_id, url=url, name=name, alias="???")
        b.save()

    def get_sql_query(self):
        return "SELECT * FROM boards"

class ForEachUser(ForEach):

    def visit_row(r):
        user_id, username, status = r
        User(pk=user_id, username=username, status=status).save()

    def get_sql_query(self):
        return "SELECT * FROM users"

class ForEachTopic(ForEach):

    def visit_row(r):
        topic_id, board_id, user_id, num, title, post_count, last_post_date, status = r
        t = Topic(pk=topic_id, board_id=board_id, user_id=user_id, gfaqs_id=num,
            number_of_posts=post_count, last_post_date=last_post_date, status=status)
        t.save()

    def get_sql_query(self):
        return "SELECT * FROM topics"

class ForEachPost(ForEach):

    def visit_row(r):
        post_id, topic_id, user_id, date, num, contents, signature, status = r
        p = Post(pk=post_id, topic_id=topic_id, user_id=user_id, date=date,
            post_num=num, contents=contents, signature=signature, status=status)
        p.save()

    def get_sql_query(self):
        return "SELECT * FROM posts"
