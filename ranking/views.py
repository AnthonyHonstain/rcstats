import re
import trueskill.trueskill as trueskill

from django.db.models import Max
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from rcstats.ranking.models import RankedClass, RankEvent, RankEventDetails, Ranking
from rcstats.rcdata.models import SingleRaceDetails, SingleRaceResults, RacerId, TrackName, SupportedTrackName


def ranking(request):
    return render_to_response('ranking.html', {}, context_instance=RequestContext(request))


REQUIRED_NUM_RACES = 10
NUM_RANK_EVENTS_TO_DISPLAY = 8


def _format_rank(rank):    
    rank = rank + 5 # I want to boost people above 0
    rank *= 2
    return round(rank, 2)


def ranking_track_class(request, rankedclass_id):
    
    rankedclass_obj = get_object_or_404(RankedClass, pk=rankedclass_id)
    
    trackname = TrackName.objects.get(pk=rankedclass_obj.trackkey.id).trackname
    classname =  rankedclass_obj.raceclass

    # Get the last ten rankings and graph them.
    
    rankevents = RankEvent.objects.filter(rankedclasskey__exact=rankedclass_obj.id)
    if (len(rankevents)  < 1):
        # We do not have anyhting to show the user.
        raise Http404
        
    latestevents = rankevents.order_by('-eventcount')[:NUM_RANK_EVENTS_TO_DISPLAY]

    current_rank_ordering = []
    
    # =======================================================================
    # Collect and format data for datable of current rankings.
    # =======================================================================
    current_ranking_formated = []
    
    datatable_ranking = Ranking.objects.filter(rankeventkey__exact=latestevents[0].id,
                                               racecount__gte=REQUIRED_NUM_RACES).order_by('-rank')
    
    count = 1
    for rank in datatable_ranking:
        current_ranking_formated.append([count, rank.raceridkey.racerpreferredname, _format_rank(rank.rank)])
        count += 1
        current_rank_ordering.append(rank.raceridkey.id)
        
    current_ranking = simplejson.dumps(current_ranking_formated) 
    
    super_group = []
    count = 0
    prev = 0
    #print "current_rank_ordering", current_rank_ordering
    for current in range(10, len(current_rank_ordering), 10):
        if (current + 10 > len(current_rank_ordering)):
            # We want to fold the rest into the final group
            current = len(current_rank_ordering)
        super_group.append({'title':"Ranks {0}-{1}".format(prev, current),
                            'js_id':str(count),
                            'ranking_graph_jsdata':None})
        
        
        # =======================================================================
        # Collect and format the date for the flot graph.
        # =======================================================================
        ranking_graphdata = {}
            
        racer_dict = {} # Hold the racers rankings { <racerid>:[25.0, 24.0, 23.0, ..]
        # WARNING - The index 0 is the most recent event, index 1 is the next most recent, etc..
            
        for rankevent in latestevents:        
            ranking = Ranking.objects.filter(rankeventkey__exact=rankevent.id,
                                             racecount__gte=REQUIRED_NUM_RACES).order_by('-rank')
            
            for rank in ranking: # This covers all the racers being ranked at this stage.
                
                # We only want to use them if they are in this grouping
                print rank.raceridkey.id
                if (rank.raceridkey.id in current_rank_ordering[prev:current]):
                    print "ping"
                    if rank.raceridkey.id in racer_dict:
                        racer_dict[rank.raceridkey.id].append(_format_rank(rank.rank))
                    else:
                        racer_dict[rank.raceridkey.id] = [None, None, _format_rank(rank.rank), ]
            
            
        # Now we need to format the ranking data for display in the flot graph.    
        for racer in racer_dict:
            
            if (len(racer_dict[racer]) < NUM_RANK_EVENTS_TO_DISPLAY):
                racer_dict[racer] += [None,] * (NUM_RANK_EVENTS_TO_DISPLAY - len(racer_dict[racer]))
                
            indv_rank_data = []
            for i in range(len(racer_dict[racer])):
                indv_rank_data.append([NUM_RANK_EVENTS_TO_DISPLAY + 2 - i, racer_dict[racer][i]])
            
            racer_name = RacerId.objects.get(pk=racer).racerpreferredname
            #racer_name = racer.racerpreferredname
            ranking_graphdata[racer_name] = {'label': racer_name,
                                             'data': indv_rank_data}                
    
        #print 'ranking_graphdata', ranking_graphdata
        ranking_graph_jsdata = simplejson.dumps(ranking_graphdata)    
        
        super_group[-1]['ranking_graph_jsdata'] = ranking_graph_jsdata
        prev = current
        count += 1
    
#    return render_to_response('rankingtrackclassdetailed.html', 
#                              {'trackname': trackname,
#                               'classname': classname, 
#                               'current_ranking': current_ranking,
#                               'ranking_graph_jsdata': ranking_graph_jsdata,}, 
#                              context_instance=RequestContext(request))
    #print super_group

    return render_to_response('rankingtrackclassdetailed.html', 
                              {'trackname': trackname,
                               'classname': classname, 
                               'current_ranking': current_ranking,
                               'super_group': super_group,}, 
                              context_instance=RequestContext(request))


def get_ranked_classes_by_track(trackkey):
    '''
    For the given track, return all the rankedclass keys that have ranked
    racers with the REQUIRED_NUM_RACES.    
    '''
    trackname_obj = TrackName.objects.get(pk=trackkey)
    
    possible_rankedclasses = RankedClass.objects.filter(trackkey__exact=trackname_obj)
    # For each of these rankedclasses, we are only concerned with
    # classes that have 2 or more racers with more than the required_num_races
    # completed.
    
    return_keys = []
    
    for rankedclass in possible_rankedclasses:
        rankevents = RankEvent.objects.filter(rankedclasskey__exact=rankedclass.id)
        latestevent = None    
        if (len(rankevents) > 0):
            latestevent = rankevents.order_by('-eventcount')[0]
            
        # We want to count the number of ranked racers with the required number of events.
        rankings = Ranking.objects.filter(rankeventkey__exact=latestevent.id,
                                          racecount__gte=REQUIRED_NUM_RACES)
        
        if (len(rankings) >= 2):
            return_keys.append(rankedclass.id)

    return return_keys




class _GroupedEvent():
    def __init__(self, rankevent=None, ranking=[]):
        self.rankevent = rankevent
        # ranking is a list or racerid's in the order they finished.
        self.ranking = ranking
    def __str__(self):
        return str(self.rankevent) + " " + str(self.ranking)
    
class _Player(object):    
    def __init__(self, racerid, skill=(25.0, 25.0/3.0), racecount=1):
        self.racerid = racerid
        self.skill = skill
        self.racecount = racecount
        self.rank = None
    
    def __str__(self):
        return "mu={0[0]:.3f}  sigma={0[1]:.3f} count={1}".format(self.skill, self.racecount)

def process_ranking(rankedclass_obj):
    '''
    For the RankedClass, we want to see if there is a new event, then process
    the races from the event and update the ranking.
    
    IMPORTANT - we only consider races that are a MAIN event
        This means it MUST have [A-Z]-Main in the class name.
        
    IMPORTANT - if you upload an older race (then the most recent one 
        being tracked in a RankEvent), then it will not be considered
        in the ranking.
        
    IMPORTANT - Quallifiers are considered as well.
    '''    
    # ===============================================================
    # Step 1 - Get the date to start looking for new races from
    # ===============================================================
    checkdate = rankedclass_obj.startdate
    print "checkdate", checkdate
        
    # ===============================================================
    # Step 2 - Get the races we want to use for ranking (if they exist)
    # ===============================================================
    # Now that we have a date to start looking for new races from,
    # we want to find and process all that we find.
    #     Remember - qualifiers are considered seperately.
    #     Main events are grouped into a single stack ranking.    
    races_to_rank = SingleRaceDetails.objects.filter(trackkey__exact=rankedclass_obj.trackkey,
                                                     racedata__contains=rankedclass_obj.raceclass,
                                                     racedata__icontains="main",
                                                     racedate__gt=checkdate).\
                                                     order_by('racedate')
            
    if (len(races_to_rank) == 0):
        # There are no new races to process ranking for.
        return
    
    # ===============================================================
    # Step 3 - Organize the races with sub-mains into a single stack rank
    # ===============================================================
    # Format for grouped_results = [ <_GroupedEvent object>, <_GroupedEvent object>, ...
    grouped_results = []
    prev_race = None
    
    # Get the most recent event for this class
    rankevents = RankEvent.objects.filter(rankedclasskey__exact=rankedclass_obj.id)
    eventcount = 0
    latestevent = None    
    if (len(rankevents) > 0):
        latestevent = rankevents.order_by('-eventcount')[0]
        eventcount = latestevent.eventcount
    print "MOST RECENT EVENT:", latestevent
            
    print "-"*30 
    print "Start Grouping"
    print "-"*30
    
    '''
    Overview of the grouping code below:
        I need to group the A,B,C mains into a single race, since that 
        day of competition is a comparison of everyone.
    
    Example - if you win the B-main, it looks the same as if you won the A,
         this is going to confuse things if we dont create a single stack
        
    '''    
    pattern = re.compile("[B-Z][1-9]? main", re.IGNORECASE)
    
    # I have the problem of grouping multiple A-mains
    # Work through the race results from OLDEST to NEWEST
    for race_details in races_to_rank:
        #print race_details.racedate
        #print eventcount + 1
        #print "grouped_results", grouped_results
        #print    
                
        # If the last race was a sub-main - we are going to combine this and
        # the previous.
        start_index = None
        if prev_race != None:
            start_index = pattern.search(prev_race.racedata)
                
        if (start_index != None):
            # We found a sub A-main race
            results = SingleRaceResults.objects.filter(raceid__exact=race_details).order_by('finalpos').values('racerid', 'finalpos')
            flatresults = []
            for result in results:
                flatresults.append(result['racerid'])
                
            grouped_results[-1].ranking = _combine_races(grouped_results[-1].ranking, flatresults)
            
            neweventdetails = RankEventDetails(rankeventkey=grouped_results[-1].rankevent, 
                                               racedetailskey=race_details)
            neweventdetails.save()            
                        
        else:            
            # Now we want to collect all the the results for this race
            results = SingleRaceResults.objects.filter(raceid__exact=race_details).order_by('finalpos').values('racerid', 'finalpos')
            flatresults = []
            for result in results:
                flatresults.append(result['racerid'])
            
            # We want to ignore races with only 1 person. There is no ranking that can be done.
            if (len(flatresults) <= 1):
                continue # We dont want to create an event for this race (NOT RANKED).
            
            eventcount += 1
            newevent = RankEvent(rankedclasskey=rankedclass_obj, eventcount=eventcount)
            newevent.save()
            
            # TODO - This would be a good place to check if this racedetails has
            # already been associated with this rankedclass. We DO NOT want
            # to have duplicates in the system. 
                        
            neweventdetails = RankEventDetails(rankeventkey=newevent, 
                                               racedetailskey=race_details)
            neweventdetails.save()
            
            grouped_results.append(_GroupedEvent(newevent, flatresults))

        prev_race = race_details

    # This is important, we want to record the date of the last race we have
    # processed.
    rankedclass_obj.startdate = prev_race.racedate
    rankedclass_obj.save()
    
    #print "New Start Date:", rankedclass_obj.startdate 

    # ===============================================================
    # Step 4 - Now we are ready to compute the ranking.
    # ===============================================================
    latestevent_ranked = latestevent
    
    for event in grouped_results:
        print "Event:", event.rankevent
        print "Ranking:",  event.ranking
        print "Number of players to rank for this event:", len(event.ranking) 
        
        player_dict = {} # Used to organize all the Player objects before we compute ranking.
    
        # We need all the currently ranked racers for this class.
        currently_ranked = Ranking.objects.filter(rankeventkey__exact=latestevent_ranked)
        for player in currently_ranked:
            player_dict[player.raceridkey.id] = _Player(player.raceridkey.id, 
                                                        skill=(player.mu, player.sigma), 
                                                        racecount=player.racecount)
        
        players_to_adjust = []
        
        # Now for each grouped race, we want to create the player objects if needed
        # and process the racers from this event (increment their racecount and set rank).
        for i in range(len(event.ranking)):
            racer = event.ranking[i]
            if racer in player_dict:
                player_dict[racer].racecount += 1
            else:
                player_dict[racer] = _Player(racer)
                
            player_dict[racer].rank = i + 1
            
            players_to_adjust.append(player_dict[racer])
                
        # We adjust the racers that were in this event.
        trueskill.AdjustPlayers(players_to_adjust)
        
        # Take the results and store them in the db, new racers will
        # also get written out.        
        for racer in player_dict.values():
            newranking = Ranking(rankeventkey = event.rankevent,
                                 raceridkey = RacerId.objects.get(pk=racer.racerid),
                                 mu = racer.skill[0] ,
                                 sigma = racer.skill[1], 
                                 # rank = mu - (3*sigma)
                                 rank = racer.skill[0] - 3*racer.skill[1],
                                 racecount = racer.racecount)
            newranking.save()
        
        latestevent_ranked = event.rankevent
        

def _combine_races(submain_results, highermain_results):
    '''
    The results from the highermain are going to be added to the submain.
    
    submain_results: the list of racerid (in the order of finalpos) [123, 5, 250, ...]
        This is the B,C,D mains
    highermain_results: the list of racerid's in the order of finalpos, this
        will be the results of a higher main. If submain is the C main,
        the highermain_results would be the B main.
    '''
    returnlist = []
    
    print "COMBINE RACES", highermain_results, submain_results
    # Fist check for bumps and remove them from the submain results.
    for higherresult in highermain_results:
        if higherresult in submain_results:
            print "FOUND BUMP:", higherresult
            submain_results.remove(higherresult)
        
    return highermain_results + submain_results