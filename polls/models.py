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
    trackname = models.CharField(max_length=200)

class SingleRaceDetails(models.Model):
    trackkey = models.ForeignKey(TrackName)
    racedata = models.CharField(max_length=200)
    roundnumber = models.IntegerField()
    racenumber = models.IntegerField()
    racedate = models.DateTimeField('date of the race')
    uploaddate = models.DateTimeField('date of the race')

# The a single racer, there name (probably not going be be unique by default)
class RacerId(models.Model):
    racerpreferredname = models.CharField(max_length=200)
    
    
class SingleRacerData(models.Model):
    raceid = models.ForeignKey(SingleRaceDetails)
    racerid = models.ForeignKey(RacerId)
    racelap = models.SmallIntegerField()
    raceposition = models.SmallIntegerField()
    racelaptime = models.DecimalField(decimal_places=3, max_digits=5)





    
