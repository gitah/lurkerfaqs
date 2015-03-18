import sys
import os
import logging

from django.core.management.base import BaseCommand, CommandError
from gfaqs.models import User, Board, Topic, Post
from django.conf import settings

class ContentVisibilityManager(object):
    """
    Manages visibility of content
    """
    def get_user(self, username):
        return User.objects.get(username=username)

    def get_topic(self, gfaqs_topic_id):
        return Topic.objects.get(gfaqs_id=gfaqs_topic_id)

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
            return user

    def hide_topic(self, topic):
        if not topic:
            return None
        else:
            topic.status = Topic.HIDDEN
            topic.save()
            return topic

    def hide_post(self, post):
        if not post:
            return None
        else:
            post.status = post.HIDDEN
            post.save()
            return post

