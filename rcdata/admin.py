from rcdata.models import SingleRaceDetails, RacerId, LapTimes
from django.contrib import admin


#class SingleRaceDetailsInLine(admin.TabularInline):
#    model = Choice
#    extra = 3

class SingleRaceDetailsAdmin(admin.ModelAdmin):
    fields = ['raceData', 'raceDate']

class LapTImesAdmin(admin.ModelAdmin):
    fields = ['raceId', 'racerId', 'raceLap', 'raceLapTime']

class RacerIdAdmin(admin.ModelAdmin):
    fields = ['racerPreferredName']


admin.site.register(SingleRaceDetails)
admin.site.register(LapTimes)
admin.site.register(RacerId)



