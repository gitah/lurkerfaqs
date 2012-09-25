from django.db import models

#TODO:
#       make `User`.`username` unique
#       make `Board`.`alias` unique
#       make `Topic`.`gfaqs_id` unique

class User(models.Model):
    NORMAL, MOD, ADMIN, HIDDEN= 0,1,2,9
    USER_STATUS = (
        (NORMAL,"normal"),
        (MOD,"mod"),
        (ADMIN,"admin"),
        (HIDDEN,"hidden")
    )
    username = models.CharField(max_length=25)
    status = models.CharField(max_length=2, choices=USER_STATUS, default=NORMAL)

class Board(models.Model):
    url = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)
    #TODO: figureout what to do with these:
    #next_update	datetime			No			 	 	 	 	 	 	
    #last_topic_date	datetime			No			 	 	 	 	 	 	
    #scrape_period	int(11)
    
class Topic(models.Model):
    NORMAL, CLOSED, ARCHIVED = 0,1,2
    STICKY, STICKY_CLOSED,PURGED,POLL = 3,4,5,6
    TOPIC_STATUS = (
        (NORMAL,"normal"),
        (CLOSED,"closed"),
        (ARCHIVED,"archived"),
        (STICKY,"sticky"),
        (STICKY_CLOSED,"sticky_closed"),
        (PURGED,"purged"),
        (POLL,"sticky_closed"),
    )
    board = models.ForeignKey(Board)
    creator = models.ForeignKey(User)
    gfaqs_id = models.CharField(max_length=15)
    title = models.CharField(max_length=200)
    number_of_posts = models.IntegerField()
    last_post_date = models.DateTimeField()
    status = models.CharField(max_length=2, choices=TOPIC_STATUS, default=NORMAL)

    def __str__(self):
        return "[%s] (Creator=%s)" % (self.title, self.creator.username)
    
class Post(models.Model):
    NORMAL, CLOSED, MODDED, EDITED = 0,1,2,3
    POST_STATUS = (
        (NORMAL,"normal"),
        (CLOSED,"closed"),
        (MODDED,"modded"),
        (EDITED,"edited")
    )
    topic = models.ForeignKey(Topic)
    creator = models.ForeignKey(User)
    date = models.DateTimeField()
    post_num = models.CharField(max_length=15)
    contents = models.TextField()
    signature = models.TextField()
    status = models.CharField(max_length=2, choices=POST_STATUS, default=NORMAL)

    def __str__(self):
        return "[%s] (Creator=%s)\n %s \n---\n %s" % (self.topic.title,
                self.creator.username, self.contents, self.signature)
