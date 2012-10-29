# -*- coding: utf-8 -*-
from django.db import models

class TopUsersTopic(models.Model):
    """ A model for the top_users batch """
    username = models.CharField(max_length=25)
    count = models.IntegerField()

class TopUsersPost(models.Model):
    """ A model for the top_users batch """
    username = models.CharField(max_length=25)
    count = models.IntegerField()
