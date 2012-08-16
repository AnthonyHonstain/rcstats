from rcstats.ranking.models import RankedClass, RankEvent, RankEventDetails, Ranking
from django.contrib import admin

class RankedClassAdmin(admin.ModelAdmin):
    list_display = ('trackkey', 'raceclass', 'startdate')
    list_filter = ['trackkey', 'raceclass']

class RankedEventAdmin(admin.ModelAdmin):
    list_display = ('rankedclasskey', 'eventcount')
    list_filter = ['rankedclasskey',]
    
class RankedEventDetailsAdmin(admin.ModelAdmin):
    list_display = ('rankeventkey', 'racedetailskey')
    
class RankingAdmin(admin.ModelAdmin):
    list_display = ('rankeventkey', 'raceridkey',  'mu', 'sigma', 'rank', 'racecount')
        
admin.site.register(RankedClass, RankedClassAdmin)
admin.site.register(RankEvent,RankedEventAdmin)
admin.site.register(RankEventDetails,RankedEventDetailsAdmin)
admin.site.register(Ranking, RankingAdmin)

