import time
import datetime

from dateutil.relativedelta import relativedelta

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.db import connection
from django.utils import simplejson

from rcdata.models import SupportedTrackName, SingleRaceDetails, SingleRaceResults



def trackdata(request):
    tracklist = SupportedTrackName.objects.all()

    return render_to_response('trackdata.html', {'track_list':tracklist})

def trackdetail(request, track_id):
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)
    
    ctx = Context({'trackname':supported_track.trackkey})
    return render_to_response('trackdatadetail.html', ctx)
    

def trackdetail_data(request, track_id, time_frame='alltime'):
    """
    the purpose of trackdetail_data is to provide summary race data about
    the track for varying periods of time. 
    
    PERFORMANCE CONCERN
        For stats that calculated Per Racer, only a set number of results
        are returned (we dont want to do every single person). 
    
    Current stats - Filtered by date, sorted by the count
        Total number of wins for the top racers
        Total number of laps for the top racers
    """
    
    # I am not assuming that the track_id provided is actually valid.
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)
    
    if (time_frame not in ('alltime', 'month', '6months')):
        raise Http404
    
    DISPLAY_RESULT_LIMIT = 100
    
    #
    # This is where we set the time period to filter by.
    #    If the filter is "All Time" there is no need to filter at all.
    sql_time_filter = ''
    filterdatestr = 'All Time'
    
    if (time_frame == 'month'):
        filterdate = datetime.datetime.now() + relativedelta(months=-1)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sql_time_filter = "AND rdetails.racedate > '" + dbdate + "'"
    elif (time_frame == '6months'):
        filterdate = datetime.datetime.now() + relativedelta(months=-6)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sql_time_filter = "AND rdetails.racedate > '" + dbdate + "'"
        
    
    # Get the total number of wins.
    topwins = _get_Total_Wins(supported_track.trackkey.id, sql_time_filter, DISPLAY_RESULT_LIMIT)

    # Get the total number of laps
    toplaps = _get_Total_Lap(supported_track.trackkey.id, sql_time_filter, DISPLAY_RESULT_LIMIT)
        
    topwins_jsdata = simplejson.dumps(topwins)
    toplaps_jsdata = simplejson.dumps(toplaps)
      
    ctx = Context({'filterdate':filterdatestr,
                   'tabid':time_frame, # For this to work with tabs, I need unique id's for each datatable
                   'topwins':topwins_jsdata, 
                   'toplaps':toplaps_jsdata})
    return render_to_response('trackdatadetail_data.html', ctx)
        
        
def _get_Total_Wins(track_key_id, sql_time_filter, row_limit):
    #
    # This query does all the work to find the total number of race wins
    #
    
    sqlquery = '''SELECT SUM(racedata.finalpos), racedata.racerpreferredname  FROM
      (
      SELECT rresults.raceid_id, rid.racerpreferredname, rresults.finalpos FROM
        rcdata_racerid as rid,
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = rid.id AND
            rresults.finalpos = 1    
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sql_time_filter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.racerpreferredname
    ORDER BY SUM(racedata.finalpos) desc
    LIMIT ''' + str(row_limit) + ''';'''
    
    cursor = connection.cursor()   
    cursor.execute(sqlquery, {'trackkey':track_key_id})
    topwins = cursor.fetchall()

    return topwins
        

def _get_Total_Lap(track_key_id, sql_time_filter, row_limit):
        
    #
    # This query does the work to find the total number of laps races.
    #
    querytoplaps = '''SELECT SUM(racedata.lapcount), racedata.racerpreferredname  FROM
      (
      SELECT rresults.raceid_id, rid.racerpreferredname, rresults.lapcount FROM
        rcdata_racerid as rid,
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = rid.id
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sql_time_filter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.racerpreferredname
    ORDER BY SUM(racedata.lapcount) desc
    LIMIT ''' + str(row_limit) + ''';'''
       
    cursor = connection.cursor()
    cursor.execute(querytoplaps, {'trackkey':track_key_id})
    toplaps = cursor.fetchall()
    
    return toplaps


def recentresultshistory(request, track_id):
    """
    Main page to organize and display the recent race results from the track.
    
    The race date is processed using the format '%Y-%m-%d'
    
    """    
    NUMBER_OF_RESULTS_FOR_HISTORY = 5
    
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)

    raw_race_dates = _get_Recent_Race_Dates(supported_track, NUMBER_OF_RESULTS_FOR_HISTORY)
    
    race_dates = []
    for index in range(NUMBER_OF_RESULTS_FOR_HISTORY):
        race_dates.append({'id':"button_" + str(index), 
                           'display_date': _display_Date_User(raw_race_dates[index]),
                           'date': raw_race_dates[index].strftime('%Y-%m-%d')})
                          
    ctx = Context({'supportedtrack':supported_track, 'race_dates':race_dates})
                                                             
    return render_to_response('recentresultshistory.html', ctx)
    


def recentresultshistory_data(request, track_id, race_date):
    """
    Will use the recentresultshistory_data.html template to display all
    of the races at the specified track_id on the given race_date.
    """
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)

    try:
        date = datetime.datetime.strptime(race_date, "%Y-%m-%d").date()
    except ValueError():
        raise Http404
    
    # Note Format (year, month, date)
    # Note - the range (date1, date2) works like date1 <= x < date2
    race_details = SingleRaceDetails.objects.filter(racedate__range=(date, 
                                                                     date + relativedelta(days=+1)),
                                                    trackkey=supported_track.trackkey).order_by('racedate')
    
    results_template_format = []
        
    #print "track", supported_track.trackkey, "date", date + relativedelta(days=+1) , 'race_details', race_details
    for race_detail in race_details:
                
        formated_result = []     
            
        race_results = SingleRaceResults.objects.filter(raceid = race_detail.id)
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
        results_template_format.append({'racedata':race_detail.racedata,
                            'roundnumber':race_detail.roundnumber,
                            'racenumber':race_detail.racenumber,
                            'racedate':race_detail.racedate,
                            'tagid':race_detail.id,
                            'individual_results':jsdata})
    
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
    ctx = Context({'trackname':supported_track.trackkey, 
                   'display_date':_display_Date_User(date), 
                   'raceresults':results_template_format})
    
    return render_to_response('recentresultshistory_data.html', ctx)


def _get_Recent_Race_Dates(supported_track, number_races):
    """
    Retrieve a list of python datetime objects for the most recent races.
    
    WARNING - Only considers race dats with a main event (racedata contains the token 'main')
    
    Note - I spent a fair bit of time trying to figure out how
    to do this type of query using the orm, but I have been unable
    to get to any where near as simple of a solution.
        Trying to do something like: SingleRaceDetails.objects.aggregate(datetime)        
    """

    querydates = '''SELECT rdetails_date.racedate::date as racedate FROM
        rcdata_singleracedetails as rdetails_date
        WHERE rdetails_date.trackkey_id = %(trackkey)s AND      
          rdetails_date.racedata ILIKE '%%main%%'
        GROUP BY rdetails_date.racedate::date
        ORDER BY rdetails_date.racedate::date desc
        LIMIT %(numraces)s;'''
       
    cursor = connection.cursor()
    cursor.execute(querydates, {'trackkey':supported_track.trackkey.id, 'numraces':number_races})
    racedates = cursor.fetchall()
    
    # Example racedates for tacoma and number_races=5:
    # [(datetime.date(2012, 5, 12),), (datetime.date(2012, 5, 11),), (datetime.date(2012, 5, 8),), 
    #  (datetime.date(2012, 5, 5),), (datetime.date(2012, 5, 4),)]
    #print 'racedates', racedates
    
    racedates_flat = [item for sublist in racedates for item in sublist]    
    return racedates_flat


def _display_Date_User(datetime_object):
    """
    Take the datetime object and generate the string to display to users.
    """
    return datetime_object.strftime('%a, %d %b %Y')