'''
Created on Nov 12, 2012

@author: Anthony Honstain
'''
import rcstats.utils as utils
from rcstats.rcdata.models import LapTimes, SupportedTrackName, SingleRaceDetails, SingleRaceResults

from django.utils import simplejson


def lap_time_history_fastest_each_night_flot_data(racedetails_obj):
    '''
    For a given race, find fastest laptimes from the class (having same race length)
    and format them for the flot graph.
    '''    
    # Get the data to display the recent race times graph
    recent_laptimes = _get_lap_time_history(racedetails_obj.trackkey, 
                                           racedetails_obj.racedata, 
                                           racedetails_obj.racelength,
                                           startdate=racedetails_obj.racedate)
    recent_laptimes_striped = []
    for i in range(len(recent_laptimes)):
        single_row = [i+1, 
                      "{0:.2f}".format(recent_laptimes[i]['formated_time']),
                      # Additional data for the tooltip
                      "{0} Laps in {1}".format(recent_laptimes[i]['lapcount'], 
                                               utils.format_racetime_for_user(recent_laptimes[i]['racetime'])),
                      utils.format_date_for_user(recent_laptimes[i]['racedate'])]
                                               
        recent_laptimes_striped.append(single_row)
    
    formated_recent_laptimes = []       
    formated_recent_laptimes.append({'label': "Recent Races", 
                                     'data': recent_laptimes_striped, 
                                     'color':"rgb(70, 120, 70)"})
       
    recent_laptimes_jsdata = simplejson.dumps(formated_recent_laptimes)
    print recent_laptimes_jsdata
    
    '''
     Example - 
     [{"color": "rgb(70, 120, 70)", 
       "data": [[1, "27.82"], ... ] 
       "label": "Recent Races"}]
    '''
    return recent_laptimes_jsdata       

def _get_lap_time_history(track, raceclass, racelength, startdate=None, racerid=None, number_of_races=50):
    '''
    Get the key race data for the track/class/racelength along with any additional
    conditions so that we can display a graphical representation of the most recent
    race results.
    IE: how did my race tonight compare to the last several weeks or racing at this track?
        
    Format the results.
         Overview - we use the laptime as the integer in the graph, then
         the race time is formated in the decimal part.
             The number of seconds is converted with the smallest number being
             closest to 1, and the largest number of seconds being closest to 0.
             
    I need to group and organize, there would be no point in
    trying to show 8min main next to 6min qual. 
         Show both? - Answer: group by race time.
         How do I deal with qualifiers (different lengths of time?)
         some are 8min some are 6mins
    '''        
    #
    # Need to filter the different classes that we want to show
    #
    # TODO - join with results table to get the racer.
    if startdate:
        details = SingleRaceDetails.objects.filter(trackkey=track,
                                                   racedata__contains=raceclass,
                                                   racedate__lte=startdate,
                                                   racelength=racelength).order_by('-racedate')[:number_of_races] 

    else:
        details = SingleRaceDetails.objects.filter(trackkey=track,
                                                   racedata__contains=raceclass,
                                                   racelength=racelength).order_by('-racedate')[:number_of_races] 

    graph_results = []
    
    # Now I have the races that we want to consider, need to
    # get the winner or specified racers times.
    # TODO - consider supplied racer id instead of winner.
    if not racerid:        
        for detail in details:
            race_result = SingleRaceResults.objects.get(raceid=detail, finalpos=1)
            
            # WARNING - HUGE ASSUMPTION/TWEAKABLE VALUE SELECTED HERE
            #     This is going to have large impact on how the results are displayed.
            
            # I need the average lap time for that race.
            #    So I need all the laps for the racer 
            # TODO - I am going to start with just the bottom 75% for the winner.
            laptimes = LapTimes.objects.filter(raceid=detail, 
                                               racerid=race_result.racerid).order_by('racelaptime')
            estimated_laptime = laptimes[int(len(laptimes) * .75)].racelaptime
                        
            graph_results.append({'singleracedetails_id':detail.id,
                                  'racerid':race_result.racerid.id,
                                  'lapcount':race_result.lapcount,
                                  'racetime':race_result.racetime,
                                  'racedate':race_result.raceid.racedate,
                                  # estimated_laptime: used to calculate the formated_time, because the 
                                  # fomarted_time is RELATIVE to the estimated_laptime
                                  'estimated_laptime':estimated_laptime,
                                  'formated_time':None})            
    
    for result in graph_results: 
        # The closer the racetime seconds are to the estimated_laptime, the closer to 0
        # If > than estimated, then set to 0
        # If seconds == 0, then set to 1
        
        # WARNING - we only consider the seconds in deciding the graph's y value.
        seconds = result['racetime'].second
        estimated = int(result['estimated_laptime'])
        
        if seconds > result['estimated_laptime']:            
            formated_time = float(result['lapcount']) 
        else:
            graph_value = float(estimated - seconds) / float(estimated) 
            formated_time = result['lapcount'] + graph_value
        
        #print 'seconds', result['racetime'].minute    
        #print 'estimated', estimated
        #print 'formated_time', formated_time
        
        result['formated_time'] = formated_time 
    return graph_results