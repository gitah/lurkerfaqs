# -*- coding: utf-8 -*-
from django.db import models

class User(models.Model):
    """Represents a gamefaqs user"""
    NORMAL, MOD, ADMIN = 0, 1, 2
    HIDDEN = 99
    USER_STATUS = (
        (NORMAL,"normal"),
        (MOD,"mod"),
        (ADMIN,"admin"),
        (HIDDEN,"hidden")
    )
    username = models.CharField(max_length=25, db_index=True, unique=True)
    status = models.CharField(max_length=2, choices=USER_STATUS, default=NORMAL)

    def __str__(self):
        return self.username

    def is_hidden(self):
        return int(self.status) == User.HIDDEN

class Board(models.Model):
    """Represents a gamefaqs board (ex. CE)"""
    url = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=200, db_index=True, unique=True)

    def __str__(self):
        return self.alias


class Topic(models.Model):
    """Represents a topic made on gameefaqs"""
    NORMAL, CLOSED, ARCHIVED = 0, 1, 2
    STICKY, STICKY_CLOSED,PURGED = 3, 4, 5
    POLL, POLL_CLOSED, POLL_ARCHIVED = 6, 7, 8
    HIDDEN = 99

    POLL_STATUSES = {POLL, POLL_CLOSED, POLL_ARCHIVED}
    ARCHIVED_STATUSES = {ARCHIVED, POLL_ARCHIVED}
    STICKY_STATUSES = {STICKY, STICKY_CLOSED}

    TOPIC_STATUS = (
        (NORMAL, "normal"),
        (CLOSED, "closed"),
        (ARCHIVED, "archived"),
        (STICKY, "sticky"),
        (STICKY_CLOSED, "sticky_closed"),
        (PURGED, "purged"),
        (POLL, "poll"),
        (POLL_CLOSED, "poll_closed"),
        (POLL_ARCHIVED, "poll_archived"),
        (HIDDEN, "hidden"),
    )
    board = models.ForeignKey(Board)
    creator = models.ForeignKey(User)
    gfaqs_id = models.CharField(max_length=15, db_index=True, unique=True)
    title = models.CharField(max_length=200)
    number_of_posts = models.IntegerField()

    # For db optimizaton, I need a composite index on this + board
    # Unfortuantely django does not support this, so I made a custom initi sql
    # file (/sql/create_index) for this
    last_post_date = models.DateTimeField()
    status = models.CharField(max_length=2, choices=TOPIC_STATUS, default=NORMAL)

    def save(self, *args, **kwargs):
        super(Topic, self).save(args, kwargs)
        # adds topic to index queue
        UnindexedTopic(topic=self).save()

    def __str__(self):
        return "[%s] (%s, %s)" % (self.title, self.gfaqs_id, self.creator.username)

    def is_hidden(self):
        return int(self.status) == Topic.HIDDEN

class Post(models.Model):
    """Represents a post made on gameefaqs"""
    NORMAL, CLOSED, MODDED, EDITED = 0, 1, 2, 3
    HIDDEN = 99
    POST_STATUS = (
        (NORMAL,"normal"),
        (CLOSED,"closed"),
        (MODDED,"modded"),
        (EDITED,"edited"),
        (HIDDEN,"hidden"),
    )
    topic = models.ForeignKey(Topic)
    creator = models.ForeignKey(User)

    # composite index (creator, date) in /sql/create_index
    date = models.DateTimeField()

    post_num = models.CharField(max_length=15)
    contents = models.TextField()
    signature = models.TextField()
    status = models.CharField(max_length=2, choices=POST_STATUS, default=NORMAL)

    def __str__(self):
        return "%s\n %s \n---\n %s" % (self.topic,
            self.contents, self.signature)

    def is_hidden(self):
        return int(self.status) == Post.HIDDEN

class UnindexedTopic(models.Model):
    """ A model for the top_users batch """
    topic = models.ForeignKey(Topic)
