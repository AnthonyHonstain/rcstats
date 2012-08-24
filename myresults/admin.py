from rcstats.rcdata.models import RacerId
from rcstats.myresults.models import FeaturedRacer
from django.contrib import admin


class FeaturedRacerAdmin(admin.ModelAdmin):
    list_display = ('racerid',)
    # raw_id_fields is needed because there are 1000+ racerid's to look through.
    raw_id_fields = ('racerid',)
    ordering = ('racerid__racerpreferredname',)

admin.site.register(FeaturedRacer, FeaturedRacerAdmin)