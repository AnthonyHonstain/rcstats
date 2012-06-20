from django.db import models
from rcstats.rcdata.models import RacerId
# Create your models here.

class FeaturedRacer(models.Model):
    racerid = models.ForeignKey(RacerId)