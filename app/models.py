from tokenize import group
from unicodedata import name
from django.db import models

# Create your models here.

class Chat(models.Model):
    content = models.CharField(max_length=1000)
    timedtamp = models.DateTimeField(auto_now=True)
    group = models.ForeignKey('Group',on_delete=models.CASCADE)

class Group(models.Model):
    name = models.CharField(max_length=225)
