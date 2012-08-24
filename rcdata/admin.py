from rcstats.rcdata.models import SingleRaceDetails, RacerId, TrackName, SupportedTrackName, OfficialClassNames, AliasClassNames
import rcstats.rcdata.database_cleanup as database_cleanup
from django.contrib import admin


def collapse_alias_classnames(modeladmin, request, queryset):
    # For every SingleRaceDetails in the queryset we want
    # to see if it is an alias, if it is, than change
    # it to the official
    database_cleanup.collapse_alias_classnames(queryset)
    
collapse_alias_classnames.short_description = "Collapse alias classnames"

class SingleRaceDetailsAdmin(admin.ModelAdmin):
    #fields = ['racedata', 'racedate']
    list_display = ('racedata', 'trackkey', 'racedate', 'roundnumber', 'racenumber')
    list_filter = ['racedate', 'trackkey']
    actions = [collapse_alias_classnames]

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
    search_fields = ('racerpreferredname',)


class SupportedTrackNameAdmin(admin.ModelAdmin):
    list_display = ('trackkey', 'trackurl')
    
class OfficialClassNamesAdmin(admin.ModelAdmin):
    list_display = ('raceclass',)

class AliasClassNamesAdmin(admin.ModelAdmin):
    list_display = ('raceclass', 'officialclass')

admin.site.register(SingleRaceDetails, SingleRaceDetailsAdmin)
#admin.site.register(LapTimes, LapTimesAdmin)
admin.site.register(RacerId, RacerIdAdmin)
admin.site.register(TrackName)
admin.site.register(SupportedTrackName, SupportedTrackNameAdmin)
admin.site.register(OfficialClassNames, OfficialClassNamesAdmin)
admin.site.register(AliasClassNames, AliasClassNamesAdmin)