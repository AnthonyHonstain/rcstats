import math

from django.template import Context
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson

import rcstats.utils as utils

from rcstats.rcdata.models import SingleRaceDetails, SingleRaceResults, RacerId, LapTimes

from rcstats.rcdata.laptimehistory import lap_time_history_fastest_each_night_flot_data


def singleraceresult(request, race_detail_id):

    race_detail = get_object_or_404(SingleRaceDetails, pk=race_detail_id)

    results_template_format = {'race_detail_id': race_detail_id,
                               'racedata': utils.format_main_event_for_user(race_detail),
                               'roundnumber': race_detail.roundnumber,
                               'racenumber': race_detail.racenumber,
                               'racedate': race_detail.racedate,}
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
    # [[1, "yoshi,harley", 28, "00:08:10.761000", "16.528", "None"], [2, "Story, Corby", 27, "00:08:01.661000", "16.725", "None"],    
    jsdata = simplejson.dumps(formated_result)
    
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
    # Example lap_time_dicts - [{'racelap': 25, 'racelaptime': None}, {'racelap': 24, 'racelaptime': None}, 
    
    
    # BUG - Isn't there a way to have the ORM just give me the raw data 
    # and not a dictionary of objects?
    lap_times = []
    laps_stats = []
    for lap in lap_time_dicts:
        lap_times.append([lap['racelap'], str(lap['racelaptime'])])
        # We are only going to consider lap times we have recorded.
        if (lap['racelaptime'] != None):
            laps_stats.append(float(lap['racelaptime']))

    # It is possible that they do now have any laps, they are the roster 
    # but may have broke or not started the race.
    if (len(laps_stats) < 2):
        ctx = Context({'laps_id_js': str(race_detail) + str(racer_id) })    
        return render_to_response('singleracerlaptimes.html', ctx)
  
        
    # Get stats numbers for this race.
    laps_stats.sort()
    
    # WARNING - we are going to ignore the first lap, since it matters to the whole race, but 
    # is distinct from the other laps we are computing these statistics on.
    laps_stats = laps_stats[1:]
    
    mean = sum(laps_stats) / len(laps_stats)
    
    # While getting the stats break them up into different series for color coding.
    lap_times.sort(key = lambda tup: tup[1])
    mylist =[]
    
    
    top5_avg = "N/A"
    top10_avg = "N/A"
    top20_avg = "N/A"
    index_processed = 0
    if (len(laps_stats) >= 5):
        top5_avg = '%0.2f' % (sum(laps_stats[:5]) / 5)
        mylist.append({'label': "Top 5", 'data': lap_times[:5], 'color':"rgb(0, 255, 0)"})
        index_processed = 5
    if (len(laps_stats) >= 10):
        top10_avg = '%0.2f' % (sum(laps_stats[:10]) / 10)
        mylist.append({'label': "Top 10", 'data': lap_times[5:10], 'color':"rgb(60, 180, 60)"})
        index_processed = 10
    if (len(laps_stats) >= 20):
        top20_avg = '%0.2f' % (sum(laps_stats[:20]) / 20)
        mylist.append({'label': "Top 20", 'data': lap_times[10:20], 'color':"rgb(70, 120, 70)"})
        index_processed = 20
        
    mylist.append({'label': "Rest", 'data': lap_times[index_processed:], 'color':"rgb(180, 180, 180)"})        
    
    
    jsdata = simplejson.dumps(mylist)    
    # Example jsdata
    # [{"color": "rgb(0, 255, 0)", "data": [[12, "15.540"], [3, "15.590"], [9, "15.600"], [19, "15.620"], [5, "15.620"]], "label": "Top 5"}, 
    #  {"color": "rgb(60, 180, 60)", "data": [[10, "15.670"], [21, "15.680"], [2, "15.730"], [8, "15.740"], [16, "15.770"]], "label": "Top 10"}, 
    #  {"color": "rgb(70, 120, 70)", "data": [[6, "15.770"], [23, "15.800"], [17, "15.850"], [26, "15.860"], [13, "15.860"], [4, "15.920"], [20, "15.930"], [11, "15.930"], [14, "15.960"], [25, "15.990"]], "label": "Top 20"}, 
    #  {"color": "rgb(180, 180, 180)", "data": [[24, "16.050"], [15, "16.070"], [27, "16.390"], [7, "16.480"], [29, "16.490"], [1, "16.840"], [22, "16.990"], [18, "18.280"], [0, "19.260"], [28, "19.880"]], "label": "Rest"}]

    
    median = laps_stats[len(laps_stats) / 2]
    def test(x): return math.pow(mean - x, 2)
    
    std_dev = '%0.2f' %  math.sqrt( sum(map(test, laps_stats)) / (len(laps_stats) - 1)) 
        
    ctx = Context({'laps_id_js': str(race_detail) + str(racer_id),
                   'jsdata':jsdata,
                   'top5_avg':top5_avg,
                   'top10_avg':top10_avg,
                   'top20_avg':top20_avg,
                   'median':median,
                   'std_dev':std_dev })
    
    return render_to_response('singleracerlaptimes.html', ctx)


def singleracedetailed(request, race_detail_id):
    """
    This view displays the a deep dive of information on a single race. 
    
    """
    racedetails_obj = get_object_or_404(SingleRaceDetails, pk=race_detail_id)
    
    racedetails_formated = {'race_detail_id': race_detail_id,
                               'racedata': utils.format_main_event_for_user(racedetails_obj),
                               'roundnumber': racedetails_obj.roundnumber,
                               'racenumber': racedetails_obj.racenumber,
                               'racedate': racedetails_obj.racedate,}
    
    details_formated_result = []     
        
    race_results = SingleRaceResults.objects.filter(raceid=racedetails_obj.id)
    
    for individual_result in race_results:
        details_formated_result.append([
                                 individual_result.finalpos, # final pos
                                 individual_result.racerid.racerpreferredname, # id
                                 individual_result.lapcount, # lapcount
                                 str(individual_result.racetime), # racetime
                                 str(individual_result.fastlap), #fastlap
                                 str(individual_result.behind) # behind              
                                 ])
        
    # EXAMPLE jsdata:
    # [[1, "yoshi,harley", 28, "00:08:10.761000", "16.528", "None"], [2, "Story, Corby", 27, "00:08:01.661000", "16.725", "None"],    
    details_jsdata = simplejson.dumps(details_formated_result)    
    racedetails_formated['individual_results'] = details_jsdata
        
    
    column_names = []    
    laptime_data = []
    laptime_graphdata = {}
    
    for individual_result in race_results:
        column_names.append( individual_result.racerid.racerpreferredname )
    
        laptimes = LapTimes.objects.filter(raceid=racedetails_obj.id, racerid = individual_result.racerid.id).order_by('racelap')
        
        indv_laptime_data = []
        for lap in laptimes:
            temp_lap = None
            if (lap.racelaptime != None):
                indv_laptime_data.append([lap.racelap, float(lap.racelaptime)])
        laptime_graphdata[individual_result.racerid.racerpreferredname] = {'label': individual_result.racerid.racerpreferredname,
                                                                           'data': indv_laptime_data}
        
        # Bug - This can be cleaned up a great deal.
        lapcount = 0
        if (laptime_data == []):
            for lap in laptimes:
                temp_lap = None
                if (lap.racelaptime != None):
                    temp_lap = float(lap.racelaptime)
                    
                laptime_data.append([lapcount, temp_lap])
                lapcount += 1
        else:
            for lap in laptimes:
                temp_lap = None
                if (lap.racelaptime != None):
                    temp_lap = float(lap.racelaptime)
                
                laptime_data[lapcount].append(temp_lap)
                lapcount += 1

            

    laptime_graph_jsdata = simplejson.dumps(laptime_graphdata)
    
    laptime_jsdata = simplejson.dumps(laptime_data)
    
    # =======================================================
    # Get the data to display the recent race times graph       
    recent_laptimes_jsdata = lap_time_history_fastest_each_night_flot_data(racedetails_obj) 
    
    ctx = Context({'race_detail_id':race_detail_id,
                   'racedetails':racedetails_formated,
                   'column_names': column_names,
                   'laptime_jsdata':laptime_jsdata,
                   'laptime_graph_jsdata':laptime_graph_jsdata,
                   'recent_laptimes_jsdata':recent_laptimes_jsdata})
    
    return render_to_response('singleracedetailed.html', ctx, context_instance=RequestContext(request))

