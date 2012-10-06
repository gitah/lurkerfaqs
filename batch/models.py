from django.db import models

class TopUsersBatch(models.Model):
    """ Each row represents a time the top_user batch is run """
    date = models.DateTimeField()

class TopUsersTopic(models.Model):
    """ A model for the top_users batch """
    username = models.CharField(max_length=25)
    count = models.IntegerField()
    batch = models.ForeignKey(TopUsersBatch)

class TopUsersPost(models.Model):
    """ A model for the top_users batch """
    username = models.CharField(max_length=25)
    count = models.IntegerField()
    batch = models.ForeignKey(TopUsersBatch)

