from django.db import models

class Community(models.Model):
    zip_code   = models.CharField(db_index=True, max_length=45)
    commu_name = models.CharField(max_length=45)
    location1  = models.CharField(max_length=45, default=None, null=True)
    location2  = models.CharField(max_length=45, default=None, null=True)
    location3  = models.CharField(max_length=45, default=None, null=True)

    class Meta:
        db_table = "communities"
