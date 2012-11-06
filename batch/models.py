# -*- coding: utf-8 -*-
from django.db import models

class UserTopicCount(models.Model):
    """ A model for the top_users batch """
    username = models.CharField(max_length=25, unique=True, db_index=True)
    count = models.IntegerField()

class UserPostCount(models.Model):
    """ A model for the top_users batch """
    username = models.CharField(max_length=25, unique=True, db_index=True)
    count = models.IntegerField()
