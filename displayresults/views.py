import time
import datetime

from dateutil.relativedelta import relativedelta

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import simplejson

from rcdata.models import SupportedTrackName, SingleRaceDetails, SingleRaceResults


def singleraceresult(request, race_detail):

    race_detail = get_object_or_404(SingleRaceDetails, pk=race_detail)
                                              
    results_template_format = {}
     
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
    results_template_format['racedata'] = race_detail.racedata
    results_template_format['roundnumber'] = race_detail.roundnumber
    results_template_format['racenumber'] = race_detail.racenumber
    results_template_format['racedate'] = race_detail.racedate
    results_template_format['tagid'] = race_detail.id
    results_template_format['individual_results'] = jsdata

    # EXAMPLE results_template_format    
    # [
    #    {
    #    'individual_results': '[[1, "yoshi,harley", 28, "00:08:10.761000", "16.528", "None"], 
    #        [2, "Story, Corby", 27, "00:08:01.661000", "16.725", "None"], 
    #        [3, "hovarter,kevin", 25, "00:08:16.037000", "17.053", "None"], 
    #        [4, "Kraus, Charlie", 20, "00:08:05.180000", "20.883", "None"], 
    #        [5, "Schoening, Bryan", 12, "00:03:57.669000", "17.760", "None"]]', 
    #    'roundnumber': 5, 
    #    'tagid': 2139, 
    #    'racenumber': 1, 
    #    'racedate': datetime.datetime(2012, 5, 12, 17, 26, 32), 
    #    'racedata': u'Mod Short Course A Main'}, 
    #    
    #    {'individual_results': ' .........
    #
    
    # [
    #    {'individual_results': 
    #        '[[8, "Frankowski, Jeff", 16, "00:06:31.934000", "18.785", "None"], 
    #          [7, "Kraus, Charlie", 21, "00:08:20.190000", "19.684", "None"],
    #          [6, "Paul, Hudson", 22, "00:08:16.823000", "19.679", "None"], 
    #          [5, "Schoening, Bryan", 24, "00:08:28.335000", "19.127", "13.823"], 
    #          [4, "peterson,dave", 24, "00:08:14.512000", "17.658", "None"], 
    #          [3, "hovarter,kevin", 25, "00:08:00.116000", "17.460", "None"],
    #          [2, "Smith, Steve", 26, "00:08:15.882000", "17.449", "12.848"], 
    #          [1, "correnti, daniel", 26, "00:08:03.034000", "17.446", "None"]]', 
    #    'roundnumber': 3, 'tagid': 60, 'racenumber': 2, 
    #    'racedate': datetime.datetime(2012, 5, 2, 17, 17, 10), 
    #     'racedata': u'Stock Short Course A1 Main'}]

    print "DEBUG", results_template_format
    ctx = Context({'result':results_template_format})
    
    return render_to_response('singleraceresult.html', ctx)