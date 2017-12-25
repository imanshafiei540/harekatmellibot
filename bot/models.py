# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class User(models.Model):
    telegram_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    state = models.CharField(max_length=255, default="start")

    def __str__(self):
        return self.username
