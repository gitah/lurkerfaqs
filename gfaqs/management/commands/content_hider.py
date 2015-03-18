# -*- coding: utf-8 -*-
import sys
import os
import logging

from django.core.management.base import BaseCommand, CommandError
from gfaqs.models import User, Board, Topic, Post
from gfaqs.admin import ContentVisibilityManager

from django.conf import settings

log = logging.getLogger(settings.ARCHIVER_LOGGER)
visibility_manager = ContentVisibilityManager()


def help():
    return "usage: content_hider [user|topic|post]\n"

def help_user():
    return "usage: content_hider user <username>\n"

def help_topic():
    return "usage: content_hider topic <gfaqs_topic_id>\n"

def help_post():
    return "usage: content_hider post <gfaqs_topic_id> <topic_num>\n"

def confirm_to_proceed():
    resp = raw_input("Proceed? [y/n]")
    if resp.lower() == "y":
        return True
    else:
        return False


def handle_user(username):
    user = visibility_manager.get_user(username)
    if not user:
        print "user %s not found" % username
    else:
        print "Hiding user %s" % user
        if confirm_to_proceed():
            visibility_manager.hide_user(user)
            print "User %s hidden" % user
        else:
            print "Aborted"


def handle_topic(gfaqs_topic_id):
    topic = visibility_manager.get_topic(gfaqs_topic_id)
    if not topic:
        print "topic %s not found" % gfaqs_topic_id
    else:
        print "Hiding topic %s" % topic
        if confirm_to_proceed():
            visibility_manager.hide_topic(topic)
            print "Topic %s hidden" % topic
        else:
            print "Aborted"

def handle_post(gfaqs_topic_id, post_num):
    post = visibility_manager.get_post(topic, post_num)
    if not post:
        print "post %s,%s not found" % (gfaqs_topic_id, post_num)
    else:
        print "Hiding post %s" % post
        if confirm_to_proceed():
            visibility_manager.hide_post(post)
            print "Post %s hidden" % post
        else:
            print "Aborted"


class Command(BaseCommand):
    args = '[user|topic|post]'
    help = 'Hides posts/topics/users'

    def handle(self, *args, **options):
        if len(args) < 1:
            print help()
            sys.exit(2)
        if args[0] == "user":
            if len(args) < 2:
                print help_user()
                sys.exit(2)
            else:
                handle_user(args[1])
        elif args[0] == "topic":
            if len(args) < 2:
                print help_topic()
                sys.exit(2)
            else:
                handle_topic(args[1])
        elif args[0] == "post":
            if len(args) < 3:
                print help_post()
                sys.exit(2)
            else:
                handle_post(args[1], args[2])
        else:
            print "unknown command"
            print help()
            sys.exit(2)
