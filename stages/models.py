import json

from django.db import models

from users.models import *
from topics.models import Topic


class Stage(models.Model):
    participants = models.CharField(max_length=200, null=True)
    select_topic = models.ForeignKey(
        Topic,
        models.CASCADE,
        related_name = "stage_topic",
        null         = True
    )
    stage_time = models.CharField(max_length=45)
    create_time = models.DateTimeField(auto_now_add=True)

    def join(self, user):
        for participant in json.loads(self.participants):
            blocked1 = BlockedUser.objects.filter(
                user = user,
                blocked = participant
            ).exists()
            blocked2 = BlockedUser.objects.filter(
                user = participant,
                blocked = user
            ).exists()

            if blocked1 or blocked2:
                return True
        else:
            return False

    class Meta:
        db_table = "stages"

class WaitingRoom(models.Model):
    waiting_user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name = "waiting_user",
        null         = True
    )
    select_stage = models.ForeignKey(
        Stage,
        models.CASCADE,
        related_name = "select_stage",
        null         = True
    )
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "waiting_rooms"

