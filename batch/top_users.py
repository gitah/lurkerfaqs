from datetime import datetime

from django.db import connection, transaction

from batch.models import TopUsersTopic, TopUsersPost, TopUsersBatch
from gfaqs.models import User


NUM_TOP_USERS=50

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class Batch(object):
    pass

class TopUsersBatch(Batch):
    def start(self):
        top_users_posts = self.get_top_users_posts()
        #top_users_topics = self.get_top_users_topics()
        import pdb; pdb.set_trace()
        pass

    def get_top_users_posts(self):
        #TODO: use django ORM to do this rather than raw sql...
        sql = "select gfaqs_user.id as creator_id, username, tcount from gfaqs_user JOIN " \
            "(select creator_id, count(*) as tcount from gfaqs_topic group by " \
            "gfaqs_topic.id) as foo order by tcount desc limit %s;" % NUM_TOP_USERS
        cursor = connection.cursor() 
        cursor.execute(sql)
        return dictfetchall(cursor)

    def get_top_users_topics(self):
        #TODO: use django ORM to do this rather than raw sql...
        sql = "select gfaqs_user.id as creator_id,username,pcount " \
            "from users natural join " \
            "(select creator_id, count(*) as pcount from posts group by user_id) " \
            "as foo order by pcount desc limit %s;" % NUM_TOP_USERS;
        cursor = connection.cursor() 
        cursor.execute(sql)
        return dictfetchall(cursor)
