from polls.models import Poll, Choice
from polls.models import SingleRaceDetails, RacerId, SingleRacerData
from django.contrib import admin

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]


#class SingleRaceDetailsInLine(admin.TabularInline):
#    model = Choice
#    extra = 3

class SingleRaceDetailsAdmin(admin.ModelAdmin):
    fields = ['raceData', 'raceDate']

class SingleRacerDataAdmin(admin.ModelAdmin):
    fields = ['raceId', 'racerId', 'raceLap', 'raceLapTime']

class RacerIdAdmin(admin.ModelAdmin):
    fields = ['racerPreferredName']

#Poll, PollAdmin, 
admin.site.register(SingleRaceDetails)
admin.site.register(SingleRacerData)
admin.site.register(RacerId)



