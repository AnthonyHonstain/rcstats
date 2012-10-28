from rcstats.rcdata.models import SingleRaceDetails, RacerId, TrackName, SupportedTrackName
from django.db import models

class RankedClass(models.Model):
    trackkey = models.ForeignKey(TrackName);
    raceclass = models.CharField(max_length=200)
    # I had hoped to have startdate as a DateField, but I need to
    # consider the time as well (to simplify multiple races on same day).
    startdate = models.DateTimeField('Date Time to start ranking from.')
    lastdate = models.DateTimeField('The most recent ranking date.')
    experation = models.IntegerField('The number of races before a ranking expires')
    requiredraces = models.IntegerField('The number of ranked races required before showing in ranking')
    def __str__(self):
        return str(self.trackkey) + " | " + self.raceclass
    
class RankEvent(models.Model):
    rankedclasskey = models.ForeignKey(RankedClass)
    eventcount = models.IntegerField("Starting with event 1, the number of ranking events.")
    def __str__(self):
        return str(self.rankedclasskey) + " | " + str(self.eventcount)
    
class RankEventDetails(models.Model):
    rankeventkey = models.ForeignKey(RankEvent)
    racedetailskey = models.ForeignKey(SingleRaceDetails)
    
class Ranking(models.Model):
    rankeventkey = models.ForeignKey(RankEvent)
    raceridkey = models.ForeignKey(RacerId)
    mu = models.FloatField()
    sigma = models.FloatField()
    displayrank = models.FloatField("Calculated using mu and sigma.")
    racecount = models.IntegerField("The number of ranked race events.")
    lastrace = models.IntegerField("The most recent RankEvent event they participated in")
    def __str__(self):
        return "(" + str(self.rankeventkey) + ") | " + str(self.raceridkey) + " | " + str(self.displayrank) 