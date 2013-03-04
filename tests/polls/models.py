from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField()

