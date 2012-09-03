from django.db import models

#TODO: fill in status
USER_STATUS = (
    (0,"u1"),
    (1,"u2"),
    (2,"u3"),
    (3,"u4")
)
TOPIC_STATUS = (
    (0,"t1"),
    (1,"t2"),
    (2,"t3"),
    (3,"t4")
)
POST_STATUS = (
    (0,"p1"),
    (1,"p2"),
    (2,"p3"),
    (3,"p4")
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
    #TODO: number_of_posts Integer
    #TODO: last_post_date DateTime
    status = models.CharField(max_length=2, choices=TOPIC_STATUS)
    
class Post(models.Model):
    topic = models.ForeignKey(Topic)
    creator = models.ForeignKey(User)
    date = models.DateTimeField()
    post_num = models.CharField(max_length=15)
    contents = models.TextField()
    signature = models.TextField()
    status = models.CharField(max_length=2, choices=POST_STATUS)


