from rcstats.ranking.models import RankedClass, RankEvent, RankEventDetails, Ranking
from rcstats.ranking.views import process_ranking
from django.contrib import admin

def admin_process_ranking(modeladmin, request, queryset):
    # For every SingleRaceDetails in the queryset process the ranking
    for ranked_class in queryset:
        process_ranking(ranked_class)
    
admin_process_ranking.short_description = "Process Ranking - ONE AT A TIME"

class RankedClassAdmin(admin.ModelAdmin):
    list_display = ('trackkey', 'raceclass', 'startdate', 'lastdate', 'experation', 'requiredraces')
    list_filter = ['trackkey', 'raceclass']
    actions = [admin_process_ranking,]

class RankedEventAdmin(admin.ModelAdmin):
    list_display = ('rankedclasskey', 'eventcount')
    list_filter = ['rankedclasskey',]
    
class RankedEventDetailsAdmin(admin.ModelAdmin):
    list_display = ('rankeventkey', 'racedetailskey')
    
class RankingAdmin(admin.ModelAdmin):
    list_display = ('rankeventkey', 'raceridkey',  'mu', 'sigma', 'displayrank', 'racecount', 'lastrace')
        
admin.site.register(RankedClass, RankedClassAdmin)
admin.site.register(RankEvent,RankedEventAdmin)
admin.site.register(RankEventDetails,RankedEventDetailsAdmin)
admin.site.register(Ranking, RankingAdmin)

