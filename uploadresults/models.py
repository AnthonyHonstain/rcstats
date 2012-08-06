from django.db import models
from django.contrib.auth.models import User
from rcdata.models import SingleRaceDetails

class UploadRecord(models.Model):
    origfilename = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User)
    ip = models.IPAddressField()
    filesize = models.BigIntegerField()
    filemd5 = models.CharField(max_length=200, null=True)
    uploaddate = models.DateTimeField('Date the file was uploaded.')
    processed = models.BooleanField()
    def __str__(self):
        return str(self.filename) + " | " +\
            str(self.user) + " | " +\
            str(self.ip) + " | " +\
            str(self.uploaddate)
    
class UploadedRaces(models.Model):
    upload = models.ForeignKey(UploadRecord)
    racedetails = models.ForeignKey(SingleRaceDetails)
