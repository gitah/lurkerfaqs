from django.db import models

USER_STATUS = (
    (0,"normal"),
    (1,"mod"),
    (2,"admin"),
    (9,"hidden")
)
TOPIC_STATUS = (
    (0,"normal"),
    (1,"closed"),
    (2,"archived"),
    (3,"sticky"),
    (4,"sticky_closed"),
    (5,"purged")
)
POST_STATUS = (
    (0,"normal"),
    (1,"closed"),
    (2,"modded"),
    (3,"edited") #TODO: write tests for this
)
class User(models.Model):
    username = models.CharField(max_length=25)
    status = models.CharField(max_length=2, choices=USER_STATUS)

class Board(models.Model):
    url = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    #TODO: figureout what to do with these:
    #next_update	datetime			No			 	 	 	 	 	 	
    #last_topic_date	datetime			No			 	 	 	 	 	 	
    #scrape_period	int(11)
    
class Topic(models.Model):
    board = models.ForeignKey(Board)
    creator = models.ForeignKey(User)
    gfaqs_id = models.CharField(max_length=15)
    title = models.CharField(max_length=200)
    number_of_posts = models.IntegerField()
    last_post_date = models.DateTimeField()
    status = models.CharField(max_length=2, choices=TOPIC_STATUS)
    
class Post(models.Model):
    topic = models.ForeignKey(Topic)
    creator = models.ForeignKey(User)
    date = models.DateTimeField()
    post_num = models.CharField(max_length=15)
    contents = models.TextField()
    signature = models.TextField()
    status = models.CharField(max_length=2, choices=POST_STATUS)
