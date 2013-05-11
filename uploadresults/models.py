from django.db import models
from django.contrib.auth.models import User
from rcstats.rcdata.models import SingleRaceDetails, TrackName

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

class EasyUploaderPrimaryRecord(models.Model):
    """
    Serves as the primary record in the easy uploader system, this tracks all the separate files
    that were uploaded (:model:`uploadresults.EasyUploadRecord`)and some basic information about the transaction.
    """
    user = models.ForeignKey(User)
    ip = models.IPAddressField()
    filecount = models.IntegerField()
    filecountsucceed = models.IntegerField()
    uploadstart = models.DateTimeField('Datetime upload was started.')
    uploadfinish = models.DateTimeField('Datetime the upload was completed.', null=True)
    trackname = models.ForeignKey(TrackName, null=True) # In the future I can see letting you set the track at the next page.

class EasyUploadRecord(models.Model):
    uploadrecord = models.ForeignKey(EasyUploaderPrimaryRecord)
    origfilename = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User)
    ip = models.IPAddressField()
    filesize = models.BigIntegerField()
    filemd5 = models.CharField(max_length=200, null=True)
    uploadstart = models.DateTimeField('Date the file was uploaded.', null=True)
    uploadfinish = models.DateTimeField('Date the file was finished uploaded and processed', null=True)
    trackname = models.ForeignKey(TrackName, null=True)
    processed = models.BooleanField('We processed some or all of the file (still possible there was an error)')
    errorenum = models.IntegerField(null=True)
    def __str__(self):
        return str(self.filename) + " | " +\
            str(self.user) + " | " +\
            str(self.ip) + " | " +\
            str(self.uploadstart) + "|" +\
            str(self.uploadfinish) + "|" +\
            str(self.processed) + "|" +\
            str(self.errorenum)

class EasyUploadedRaces(models.Model):
    """
    Stores the relationship between the original file that was uploaded :model:`uploadresults.EasyUploadRecord`
    and the race record we store in the db :model:`rcdata.SingleRaceDetails`
    """
    upload = models.ForeignKey(EasyUploadRecord)
    racedetails = models.ForeignKey(SingleRaceDetails)
    
class UploadedRaces(models.Model):
    """
    Stores the relationship between the original file that was uploaded :model:`uploadresults.UploadRecord`
    and the race record we store in the db :model:`rcdata.SingleRaceDetails`
    """
    upload = models.ForeignKey(UploadRecord)
    racedetails = models.ForeignKey(SingleRaceDetails)
