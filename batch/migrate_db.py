import argparse

import MySQLdb

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

    @transaction.commit_on_success
    def start(self):
        pass
