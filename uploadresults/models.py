from django.db import models
from django.contrib.auth.models import User

class UploadRecord(models.Model):
    origfilename = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User)
    ip = models.IPAddressField()
    filesize = models.BigIntegerField()
    filemd5 = models.CharField(max_length=200, null=True)
    uploaddate = models.DateTimeField('Date the file was uploaded.')
    processed = models.BooleanField()
