# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import connection, transaction
from django.db.models import Count

from batch.models import UserTopicCount, UserPostCount
from gfaqs.models import User, Topic, Post
from batch.batch_base import Batch

class UserCountBatch(Batch):
    """Scans through all users and gets the count of posts and topics made for
    each user.

    Saves the result to the database. This data is used for the top user page
    and user profile page. SQL queries for counting this will take to long to
    run in real time.
    """

    @transaction.commit_on_success
    def start(self):
        self.clear_table()

        user_post_count = self.get_user_post_count()
        for user in user_post_count:
            tut = TopUsersTopic(username=user.username, count=user.num_topics)
            tut.save()

        user_topic_count = self.get_user_topic_count()
        for user in user_topic_count:
            tup = TopUsersPost(username=user.username, count=user.num_posts)
            tup.save()

    def clear_table(self):
        UserTopicCount.objects.all().delete()
        UserPostCount.objects.all().delete()

    def get_user_post_count(self):
        return User.objects.annotate(num_posts=Count("post"))

    def get_user_topic_count(self):
        return User.objects.annotate(num_topics=Count("topic"))
