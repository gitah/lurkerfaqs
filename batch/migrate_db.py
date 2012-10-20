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
        conn = connect(host=self.host, user=self.db_user, passwd=self.db_password)
        conn.cursor()

    @transaction.commit_on_success
    def migrate_boards(self):
        pass

    @transaction.commit_on_success
    def migrate_users(self):
        pass

    @transaction.commit_on_success
    def migrate_topics(self):
        pass

    @transaction.commit_on_success
    def migrate_posts(self):
        pass
