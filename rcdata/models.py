from django.db import models

class TrackName(models.Model):
    trackname = models.CharField(max_length=200)    
    def __str__(self):
        return str(self.trackname)

class SupportedTrackName(models.Model):
    trackkey = models.ForeignKey(TrackName)
    trackurl = models.URLField()
    # I am going to pass on this for now, this seems like alot of work.
    #trackimage = models.FilePathField(path="//home/asymptote/Desktop/RCRacePerformance/rcdata_media/images")

# A single racer, their name (probably not going be be unique by default)
class RacerId(models.Model):
    racerpreferredname = models.CharField(max_length=200)
    
class SingleRaceDetails(models.Model):
    trackkey = models.ForeignKey(TrackName)
    racedata = models.CharField(max_length=200)
    # roundnumber and racenumber do not exist in older formats
    roundnumber = models.IntegerField(null=True)
    racenumber = models.IntegerField(null=True)
    racedate = models.DateTimeField('Date of the race')
    uploaddate = models.DateTimeField('Date the race was uploaded')
    racelength = models.IntegerField('Number of minutes for the race')
    winninglapcount = models.IntegerField('Number of laps that won the race')

class SingleRaceResults(models.Model):
    raceid = models.ForeignKey(SingleRaceDetails)
    racerid = models.ForeignKey(RacerId)
    carnum = models.SmallIntegerField('Car number for this race')
    lapcount = models.SmallIntegerField('Number of laps they completed')
    racetime = models.TimeField(null=True)
    fastlap = models.DecimalField(decimal_places=3, max_digits=6, null=True)
    behind = models.DecimalField(decimal_places=3, max_digits=6, null=True)
    finalpos = models.SmallIntegerField('Final race position')
    
class LapTimes(models.Model):
    raceid = models.ForeignKey(SingleRaceDetails)
    racerid = models.ForeignKey(RacerId)
    racelap = models.SmallIntegerField()
    raceposition = models.SmallIntegerField(null=True)
    racelaptime = models.DecimalField(decimal_places=3, max_digits=6, null=True)





    
