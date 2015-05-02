import sys
import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.conf import settings
from django.db import transaction

from gfaqs.models import User, Board, Topic, Post

class ContentVisibilityManager(object):
    """
    Manages visibility of content
    """
    def clear_cache(self):
        cache.clear()

    def get_user(self, username):
        return User.objects.get(username=username)

    def get_topics_for_user(self, user):
        qs = Topic.objects.filter(creator=user).order_by('-last_post_date')
        return qs.all()

    def get_posts_for_user(self, user):
        qs = Post.objects.filter(creator=user).order_by('-date')
        return qs.all()

    def get_topic(self, gfaqs_topic_id):
        return Topic.objects.get(gfaqs_id=gfaqs_topic_id)

    def get_posts_for_topic(self, topic):
        qs = Post.objects.filter(topic=topic).order_by('date')
        return qs.all()

    def get_post(self, gfaqs_topic_id, post_num):
        topic = Topic.objects.get(gfaqs_id=gfaqs_topic_id)
        if not topic:
            return None
        return Post.objects.get(topic=topic, post_num=post_num)

    def hide_user(self, user):
        if not user:
            return None
        else:
            user.status = User.HIDDEN
            user.save()
        for topic in self.get_topics_for_user(user):
            self.hide_topic(topic)
        for post in self.get_posts_for_user(user):
            self.hide_post(post)
        self.clear_cache()
        return user

    def hide_topic(self, topic):
        if not topic:
            return None
        with transaction.atomic():
            for post in self.get_posts_for_topic(topic):
                self.hide_post(post)
            topic.status = Topic.HIDDEN
            topic.save()
        self.clear_cache()
        return topic

    def hide_post(self, post):
        if not post:
            return None
        else:
            post.status = post.HIDDEN
            post.save()
        self.clear_cache()
        return post

