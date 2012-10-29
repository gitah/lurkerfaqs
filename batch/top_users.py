# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import connection, transaction
from django.db.models import Count

from batch.models import TopUsersTopic, TopUsersPost
from gfaqs.models import User, Topic, Post
from batch.batch_base import Batch


NUM_TOP_USERS=50

class TopUsersBatch(Batch):
    @transaction.commit_on_success
    def start(self):
        self.clear_table()
        top_users_posts = self.get_top_users_posts()
        top_users_topics = self.get_top_users_topics()

        for user in top_users_topics:
            tut = TopUsersTopic(username=user.username, count=user.num_topics)
            tut.save()

        for user in top_users_posts:
            tup = TopUsersPost(username=user.username, count=user.num_posts)
            tup.save()

    def clear_table(self):
        TopUsersPost.objects.all().delete()
        TopUsersTopic.objects.all().delete()

    def get_top_users_posts(self):
        return User.objects.annotate(num_posts=Count("post"))[:NUM_TOP_USERS]

    def get_top_users_topics(self):
        return User.objects.annotate(num_topics=Count("topic"))[:NUM_TOP_USERS]
