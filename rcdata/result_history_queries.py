'''
Created on May 12, 2013

@author: asymptote
'''
from dateutil.relativedelta import relativedelta

from django.utils import simplejson

import rcstats.utils as utils
from rcstats.rcdata.models import SingleRaceDetails, SingleRaceResults

def qualifying_by_raceday_lookup(supported_track, date):
    '''
    Retrieve a list of links and descriptions for the qualifying from the specified day.
    
    Example qual_results
    [
        {
        'racedetail_id': 23, # For creating a link to the details page.
        'racedata_summary': 'Stock Buggy - Round:1  Race:3', # The description for the user.
        },
        ...
    
    '''
    qual_details = SingleRaceDetails.objects.filter(racedate__range=(date, date + relativedelta(days=+1)),
                                                    trackkey=supported_track.trackkey,
                                                    mainevent=None).order_by('racedate')
    qual_results = []
    for qual in qual_details:
        classname_summary = utils.format_main_event_for_user(qual) + \
            " - Round:" + str(qual.roundnumber) + \
            " Race:" + str(qual.racenumber)
        
        qual_results.append({'racedetail_id':qual.id,
                             'racedata_summary':classname_summary})
    return qual_results
    
def main_event_by_raceday_lookup(supported_track, date):
    '''
    Retrieve all the main events from the supported_track on the date specified.
    
    EXAMPLE results_template_format    
    [
       {
       'individual_results': '[[1, "yoshi,harley", 28, "00:08:10.761000", "16.528", "None"], 
           [2, "Story, Corby", 27, "00:08:01.661000", "16.725", "None"], 
           [3, "hovarter,kevin", 25, "00:08:16.037000", "17.053", "None"], 
           [4, "Kraus, Charlie", 20, "00:08:05.180000", "20.883", "None"], 
           [5, "Schoening, Bryan", 12, "00:03:57.669000", "17.760", "None"]]', 
       'roundnumber': 5, 
       'tagid': 2139, 
       'racenumber': 1, 
       'racedate': datetime.datetime(2012, 5, 12, 17, 26, 32), 
       'racedata': u'Mod Short Course A Main'}, 
        
       {'individual_results': ' .........
    
    '''
    # Note - Date Format (year, month, date)
    race_details = SingleRaceDetails.objects.filter(racedate__range=(date, date + relativedelta(days=+1)),
                                                    trackkey=supported_track.trackkey,
                                                    mainevent__gte=1).order_by('racedate')
    
    # Note - the range (date1, date2) works like date1 <= x < date2
    results_template_format = []
        
    #print "track", supported_track.trackkey, "date", date + relativedelta(days=+1) , 'race_details', race_details
    for race_detail in race_details:
                
        formated_result = []     
            
        race_results = SingleRaceResults.objects.filter(raceid=race_detail.id)
        for individual_result in race_results:
    
            formated_result.append([
                                     individual_result.finalpos, # final pos
                                     individual_result.racerid.racerpreferredname, # id
                                     individual_result.lapcount, # lapcount
                                     str(individual_result.racetime), # racetime
                                     str(individual_result.fastlap), #fastlap
                                     str(individual_result.behind) # behind              
                                     ])
            
        # EXAMPLE jsdata:
        # [[1, "yoshi,harley", 28, "00:08:10.761000", "16.528", "None"], [2, "Story, Corby", 27, "00:08:01.661000", "16.725", "None"], [3, "hovarter,kevin", 25, "00:08:16.037000", "17.053", "None"], [4, "Kraus, Charlie", 20, "00:08:05.180000", "20.883", "None"], [5, "Schoening, Bryan", 12, "00:03:57.669000", "17.760", "None"]]
        jsdata = simplejson.dumps(formated_result)
            
        # Going to do extra formating here, to simplify the template.
        results_template_format.append({'racedetail_id':race_detail.id,
                                        'racedata':utils.format_main_event_for_user(race_detail),
                                        'roundnumber':race_detail.roundnumber,
                                        'racenumber':race_detail.racenumber,
                                        'racedate':race_detail.racedate,                            
                                        'individual_results':jsdata})
    
    return results_template_format
