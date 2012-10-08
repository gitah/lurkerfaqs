from datetime import datetime

from django.db import connection, transaction
from django.db.models import Count

from batch.models import TopUsersTopic, TopUsersPost, TopUsersBatch
from gfaqs.models import User, Topic, Post


NUM_TOP_USERS=50

class Batch(object):
    """ Abstract class for batches """
    def start(self):
        """ Entry point to batch; override this method in subclass """
        pass

class TopUsersBatch(Batch):
    @transaction.commit_on_success
    def start(self):
        top_users_posts = self.get_top_users_posts()
        top_users_topics = self.get_top_users_topics()

        batch = TopUsersBatch(date=datetime.now())
        for user in top_users_topics:
            tut = TopUserTopic(batch=batch,
                username=user.username, count=user.num_topics)
            tut.save()

        for user in top_users_topics:
            tup = TopUserPost(batch=batch,
                username=user.username, count=user.num_posts)
            tup.save()

    def get_top_users_posts(self):
        return User.objects.annotate(num_posts=Count("post"))[:NUM_TOP_USERS]

    def get_top_users_topics(self):
        return User.objects.annotate(num_topics=Count("topic"))[:NUM_TOP_USERS]
