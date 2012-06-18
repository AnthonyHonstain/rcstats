import math

from django.template import Context
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson

from rcstats.rcdata.models import SingleRaceDetails, SingleRaceResults, RacerId, LapTimes


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
    # 
    #    {
    #    'individual_results': 
    #        '[[1, "yoshi,harley", 28, "00:08:10.761000", "16.528", "None"], 
    #          [2, "Story, Corby", 27, "00:08:01.661000", "16.725", "None"], 
    #          [3, "hovarter,kevin", 25, "00:08:16.037000", "17.053", "None"], 
    #          [4, "Kraus, Charlie", 20, "00:08:05.180000", "20.883", "None"], 
    #          [5, "Schoening, Bryan", 12, "00:03:57.669000", "17.760", "None"]]', 
    #    'roundnumber': 5, 
    #    'tagid': 2139, 
    #    'racenumber': 1, 
    #    'racedate': datetime.datetime(2012, 5, 12, 17, 26, 32), 
    #    'racedata': u'Mod Short Course A Main'
    #    }, 
    #    
    #    {'individual_results': ' .........
    #
    
    #print "DEBUG", results_template_format
    ctx = Context({'result':results_template_format})
    
    return render_to_response('singleraceresult.html', ctx, context_instance=RequestContext(request))


def singleracerlaps(request, race_detail, racer_id):
    """
    The goal is to display a bar chart of the lap times for the racer.
    
    The required information is the race (singleracedetails) and racer id
    (racerid).
    """
    
    racer_obj = get_object_or_404(RacerId, pk=racer_id)
    
    racedetails_obj = get_object_or_404(SingleRaceDetails, pk=race_detail)
    
    
    # These are all the laps for that racer.
    lap_time_dicts = LapTimes.objects.filter(raceid = racedetails_obj.id, racerid = racer_obj.id).values('racelap', 'racelaptime')        
    
    # BUG - Isn't there a way to have the ORM just give me the raw data 
    # and not a dictionary of objects?
    lap_times = []
    laps_stats = []
    for lap in lap_time_dicts:
        lap_times.append([lap['racelap'], str(lap['racelaptime'])])
        # We are only going to consider lap times we have recorded.
        if (lap['racelaptime'] != None):
            laps_stats.append(float(lap['racelaptime']))
        
    #print 'lap_times', lap_times
    
    #
    # TODO WARNING- this is prototype code, so until I fix the open bug
    # with this functionality, I will leave this block.
    #
#    # Create the data in the JSON format for the flot graph.
#    # Warning - This is not arbitrary, it is this way for a reason.
#    #mylist =[{'label': racer_obj.racerpreferredname, 'data': lap_times},]
#    mylist =[{'label': racer_obj.racerpreferredname, 'data': lap_times},
#             {'label':'stubby', 'data': [0, "5.00"]}
#             ]
#   
#    jsdata = simplejson.dumps(mylist)    
    
    # EXAMPLE - 
    # [{"data": [[27, "None"], [26, "None"], [25, "None"], [24, "None"], [23, "None"], [22, "24.800"], 
    #[21, "24.390"], [20, "19.420"], [19, "24.320"], [18, "19.150"], [17, "20.260"], [16, "25.550"], 
    #[15, "23.630"], [14, "22.910"], [13, "18.900"], [12, "18.850"], [11, "25.730"], [10, "18.500"], 
    #[9, "19.540"], [8, "18.120"], [7, "18.260"], [6, "19.620"], [5, "20.550"], [4, "18.840"], 
    #[3, "21.810"], [2, "26.720"], [1, "19.040"], [0, "33.510"]], "label": "honstain, grace"}] ;    
        
    # Get stats numbers for this race.
    laps_stats.sort()
    mean = sum(laps_stats) / len(laps_stats)
    
    # While getting the stats break them up into different series for color coding.
    lap_times.sort(key = lambda tup: tup[1])
    mylist =[]
    
    
    top5_avg = "N/A"
    top10_avg = "N/A"
    top20_avg = "N/A"
    index_processed = 0
    if (len(laps_stats) >= 5):
        top5_avg = str(sum(laps_stats[:5]) / 5)
        mylist.append({'label': "Top 5", 'data': lap_times[:5], 'color':"rgb(0, 255, 0)"})
        index_processed = 5
    if (len(laps_stats) >= 10):
        top10_avg = str(sum(laps_stats[:10]) / 10)
        mylist.append({'label': "Top 10", 'data': lap_times[5:10], 'color':"rgb(60, 180, 60)"})
        index_processed = 10
    if (len(laps_stats) >= 20):
        top20_avg = str(sum(laps_stats[:20]) / 20)
        mylist.append({'label': "Top 20", 'data': lap_times[10:20], 'color':"rgb(70, 120, 70)"})
        index_processed = 20
        
    mylist.append({'label': "Rest", 'data': lap_times[index_processed:], 'color':"rgb(180, 180, 180)"})        
    
    
    jsdata = simplejson.dumps(mylist)    
        
    
    median = laps_stats[len(laps_stats) / 2]
    def test(x): return math.pow(mean - x, 2)
    
    std_dev = math.sqrt( sum(map(test, laps_stats)) / (len(laps_stats) - 1))   
        
    ctx = Context({'laps_id_js': str(race_detail) + str(racer_id),
                   'jsdata':jsdata,
                   'top5_avg':top5_avg,
                   'top10_avg':top10_avg,
                   'top20_avg':top20_avg,
                   'median':median,
                   'std_dev':std_dev })
    
    return render_to_response('singleracerlaptimes.html', ctx)