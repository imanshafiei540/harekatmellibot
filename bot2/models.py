# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class UserQ(models.Model):
    telegram_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    state = models.CharField(max_length=255, default="start")
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Question(models.Model):
    number = models.IntegerField(null=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return str(self.number)


class Choices(models.Model):
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    correct_for_question = models.IntegerField(default=0)
    number = models.IntegerField(null=True)
    text = models.CharField(max_length=30)