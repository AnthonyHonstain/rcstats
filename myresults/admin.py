from rcstats.rcdata.models import RacerId
from rcstats.myresults.models import FeaturedRacer
from django.contrib import admin


class FeaturedRacerAdmin(admin.ModelAdmin):
    list_display = ('racerid',)

admin.site.register(FeaturedRacer, FeaturedRacerAdmin)