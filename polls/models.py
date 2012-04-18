from django.db import models
import datetime

class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.question

    def was_published_today(self):
        return self.pub_date.date() == datetime.date.today()


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()
    
    def __unicode__(self):
        return self.choice

class TrackName(models.Model):
    trackName = models.CharField(max_length=200)

class SingleRaceDetails(models.Model):
    trackName = models.ForeignKey(TrackName)
    raceData = models.CharField(max_length=200)
    roundNumber = models.IntegerField()
    raceNumber = models.IntegerField()
    raceDate = models.DateTimeField('date of the race')
    uploadDate = models.DateTimeField('date of the race')

# The a single racer, there name (probably not going be be unique by default)
class RacerId(models.Model):
    racerPreferredName = models.CharField(max_length=200)
    
    
class SingleRacerData(models.Model):
    raceId = models.ForeignKey(SingleRaceDetails)
    racerId = models.ForeignKey(RacerId)
    raceLap = models.SmallIntegerField()
    racePosition = models.SmallIntegerField()
    raceLapTime = models.DecimalField(decimal_places=3, max_digits=5)





    