from django.db import models

class User(models.Model):
    user_email     = models.EmailField(max_length=45)
    user_nickname  = models.CharField(max_length=45)
    user_password  = models.CharField(max_length=200, null=True)
    social_id      = models.IntegerField(null=True)

    class Meta:
        db_table = "users"

