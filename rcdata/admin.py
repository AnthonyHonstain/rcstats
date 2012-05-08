from rcdata.models import SingleRaceDetails, RacerId, SupportedTrackName
from django.contrib import admin


class SingleRaceDetailsAdmin(admin.ModelAdmin):
    #fields = ['racedata', 'racedate']
    list_display = ('racedata', 'trackkey', 'racedate', 'roundnumber', 'racenumber')
    list_filter = ['racedate', 'trackkey']

'''
LapTimesAdmin is disabled for now, I think there is to much data here to
expose it in a useful way in the admin (500k rows..)
'''
#class LapTimesAdmin(admin.ModelAdmin):
#    fields = ['raceId', 'racerId', 'raceLap', 'raceLapTime']

class RacerIdAdmin(admin.ModelAdmin):
    fields = ['racerpreferredname']
    # Showing the pref name gives the admin useful info.
    list_display = ('racerpreferredname',) 


class SupportedTrackNameAdmin(admin.ModelAdmin):
    list_display = ('trackkey', 'trackurl')

admin.site.register(SingleRaceDetails, SingleRaceDetailsAdmin)
#admin.site.register(LapTimes, LapTimesAdmin)
admin.site.register(RacerId, RacerIdAdmin)
#admin.site.register(TrackName)
admin.site.register(SupportedTrackName, SupportedTrackNameAdmin)

