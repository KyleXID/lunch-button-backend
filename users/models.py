from django.db import models

class User(models.Model):
    user_email     = models.EmailField(max_length=45)
    user_nickname  = models.CharField(max_length=45)
    user_password  = models.CharField(max_length=200, null=True)
    social_id      = models.IntegerField(null=True)
    summary        = models.TextField(null=True) 
    block_users    = models.ManyToManyField(
        "self", 
        through        = "BlockedUser",
        through_fields = ("user", "blocked"),
        related_name   = "user",
        symmetrical    = False
    )

    class Meta:
        db_table = "users"

class BlockedUser(models.Model):
    user    = models.ForeignKey(
        User, 
        on_delete    = models.CASCADE,
        related_name = "current_user" 
    )
    blocked = models.ForeignKey(
        User, 
        on_delete    = models.CASCADE,
        related_name = "blocked_user"
    )

    class Meta:
        #unique_together = ("user", "blocked")
        db_table = "blocked_users"
