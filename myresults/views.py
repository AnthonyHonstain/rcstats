import time
import datetime
import re

from dateutil.relativedelta import relativedelta

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.db import connection
from django.db.models import Count
from django.db.models import Q
from django.utils import simplejson

from rcdata.models import RacerId, TrackName, SupportedTrackName, SingleRaceDetails, SingleRaceResults



def myresults(request):
    
    racer_names = RacerId.objects.all()

    return render_to_response('myresults.html', {'racer_names':racer_names})

def generalstats(request, racer_id):
    racer_obj = get_object_or_404(RacerId, pk=racer_id)
    
    
    # -----------------------------------------------------------
    # Get the data for the timeline of all race results.
    # -----------------------------------------------------------
    
    # This is every race result for this racer.
    race_results = SingleRaceResults.objects.filter(racerid = racer_obj.id)        
    '''
    IMPORTANT FOR FLOT GRAPHS
    
    The timestamps must be specified as Javascript timestamps, as
      milliseconds since January 1, 1970 00:00. This is like Unix
      timestamps, but in milliseconds instead of seconds (remember to
      multiply with 1000!)
    '''    
    graphdata = []
    # Example graphdata
    #     [[1330727163000.0, 1], [1330727881000.0, 7], [1313339287000.0, 5], ... ]
    for result in race_results:
        race_detail = SingleRaceDetails.objects.get(pk = result.raceid.id)
        
        # Convert to milliseconds
        formatedtime = time.mktime(race_detail.racedate.timetuple()) * 1000        
        graphdata.append([formatedtime, result.finalpos])

    #print 'graphdata', graphdata
    mylist =[
        {'label': racer_obj.racerpreferredname, 'data': graphdata},        
    ]
    jsdata = simplejson.dumps(mylist)
            
    # -----------------------------------------------------------
    # Identify and group the race classes
    # -----------------------------------------------------------     
    # A dictionary of class names {u'MODIFIED SHORT COURSE': 4, u'STOCK BUGGY': 105,
    unique_classes = {}

    racedetails_allmains = SingleRaceDetails.objects.filter(singleraceresults__racerid = racer_obj.id,
                                            racedata__icontains = "main").values('racedata').\
                                                annotate(dcount=Count('racedata')).\
                                                order_by('dcount')[::-1]
        
    cleaned_classnames = _get_Cleaned_Class_Names(racedetails_allmains)
        
    # Now I have the unique class names and their count, I need to 
    # display this information to the user.           
    class_frequency = cleaned_classnames.items()
    class_frequency.sort(key = lambda tup: tup[1], reverse = True)
    # Example of class_frequency [(u'STOCK BUGGY', 105), (u'STOCK TRUCK', 62), 


    # -----------------------------------------------------------
    # Find last 5 races for each class and track.
    # -----------------------------------------------------------    
    '''
    There are a couple of issues to work through here.
        TO START WITH - I WILL FILTER BY LAST 2 Months to find
        the tracks and classes. Then once I have filtered by
        that I will show the last 5 races (how ever old they are).
        
    1. Find the tracks they have raced at.
    2. Find the classes they have raced in at each track.
    3. Present the last 5 races based on 1 and 2.
        GOING TO USE 'main' in the title for now, since double and trip mains do happen.
        
    [
        {
         "js_id": <>
         "trackname": <>,
         "classes: [
                    {"js_id":<>
                     "classname": <>,
                     "individual_racedata": [
                                             {'date':<>, 'id':<>, "js_id":<>}, 
                                             ...
                                            ]
                    }
                    ... Multiple classes
                   ]
         }
         ... Multiple tracks 
    ]
    
    This can be used then to construct the display for the user, with another page
    handling the lookup and display of race results for that day.
    Each racedate button displayed to the user, will show them the last race.
       
    '''
    
    # Example [{'classes': 
    #            [{'classname': u'Stock Short Course', 'individual_racedata': [60, 3334, 1005, 1001, 1766]}, 
    #             {'classname': u'Mod Short Course', 'individual_racedata': [2139, 2468, 1443, 3336, 1026]}, 
    #             {'classname': u'Stock Buggy', 'individual_racedata': [2470, 1444, 59, 3333, 1023]}], 
    #           'trackname': u'Bremerton R/C Raceway'}]
    recent_race_data = []
        
    # Get the date from 2 months ago.
    filterdate = datetime.datetime.now() + relativedelta(months=-2)
    filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
    dbdate = time.strftime('%Y-%m-%d', filterdate.timetuple())
    #sql_time_filter = "AND rdetails.racedate > '" + dbdate + "'"
    
    racetracks = SingleRaceDetails.objects.filter(racedate__gte=dbdate,
                                                  singleraceresults__racerid=racer_obj.id).values('trackkey').annotate()
    
    js_id_track = 0
                                                  
    for track in racetracks:
        #print 'track', track        
        trackname = TrackName.objects.get(pk=track['trackkey'])
        
        recent_race_data.append({'trackname': trackname.trackname, 'classes': [], 'js_id':js_id_track})
        js_id_track += 1

        # We need the class names as they will be present to the user.
        test = SingleRaceDetails.objects.filter(trackkey=track['trackkey'], # track
                                                racedate__gte=dbdate, # date
                                                singleraceresults__racerid=racer_obj.id, # racer
                                                racedata__icontains = "main" # class name
                                                ).values('racedata').annotate(dcount=Count('racedata')).order_by('dcount')[::-1]
        
        cleaned_classnames = _get_Cleaned_Class_Names(test)
        
        # NOTE - For the time being I am not going to worry about providing a recent
        # summary of race history. 
        '''
        # Now I have the unique class names and their count, I need to 
        # display this information to the user.           
        class_frequency = cleaned_classnames.items()
        class_frequency.sort(key = lambda tup: tup[1], reverse = True)
        # Example of class_frequency [(u'STOCK BUGGY', 105), (u'STOCK TRUCK', 62), 
        '''
        js_id_class = 0

        for unique_class in cleaned_classnames.keys():
            #print 'unique class', unique_class
                       
            class_dict = {'classname':unique_class, 'individual_racedata':[], 'js_id':js_id_class}
            js_id_class += 1
            
            # Now I have a track, and a class name.
            # I want the last 5 races.
            racedetails = SingleRaceDetails.objects.filter(Q(racedata__icontains="main") & Q(racedata__icontains=unique_class),
                                                           trackkey=track['trackkey'],
                                                           singleraceresults__racerid=racer_obj.id                                                           
                                                           ).order_by('racedate')[::-1][:5] 
            
            js_id_race = 0
            
            for race in racedetails:
                race_dict = {'id':race.id, 'date':_display_Date_User(race.racedate), 'js_id':js_id_race}
                js_id_race += 1
                
                class_dict['individual_racedata'].append(race_dict)
                # Now that I have the races, I need to pick the groups, and what to display.
                #print 'racedetails', race.id, 'racedata', race.racedata, 'date', race.racedate
       
            
            recent_race_data[-1]['classes'].append(class_dict)
            
            
    print recent_race_data
        
    
    ctx = Context({'racername':racer_obj.racerpreferredname, 
                   'jsdata':jsdata, 
                   'class_frequency':class_frequency,
                   'recent_race_data':recent_race_data})
    
    return render_to_response('generalstats.html', ctx)


def _get_Cleaned_Class_Names(raw_racedata_list):
    """
    Takes a list of (dictionaries) racedata and their counts, and finds 
    distinct classes from the potentially dirtied names in the race details
        Example of extraction:
            "mod buggy A2 main":2  -> "mod buggy": 2
            "mod buggy A main":5  -> "mod buggy": 7
            
    """
    
    # A dictionary of class names {u'MODIFIED SHORT COURSE': 4, u'STOCK BUGGY': 105,
    unique_classes = {}
    
    # I am going to go through the list and remove 'duplicates'
    # Example of the data befor I work with it:
    #    [{'dcount': 86, 'racedata': u'STOCK BUGGY A Main'},
    #    {'dcount': 56, 'racedata': u'STOCK TRUCK A Main'},
    #    {'dcount': 51, 'racedata': u'13.5 STOCK SHORT COURSE A Main'}]
        
    for race_dict in raw_racedata_list:            
        # I no longer care about the 'A','B', '1', 'main' etc. I am going to strip
        # and trim the strings as I add them to a new master table.            
        pattern = re.compile("[A-Z][1-9]? main", re.IGNORECASE)
        
        start_index = pattern.search(race_dict['racedata']).start(0)
        
        # We want to trim off the 'A main' part of the string and clean it up.
        processed_classname = race_dict['racedata'][:start_index].strip('+- ')
        unique_classes[processed_classname] = unique_classes.get(processed_classname, 0) + race_dict['dcount']

    return unique_classes


def _display_Date_User(datetime_object):
    """
    Take the datetime object and generate the string to display to users.
    """
    return datetime_object.strftime('%a, %d %b %Y')

"""
def myresults(request):
    
    '''
     TESTING -
    Going to try and inject json here, this is what was in the .js file.
    var data = [
        {label: 'foo', data: [[1,300], [2,300], [3,300], [4,300], [5,300]]},
        {label: 'bar', data: [[1,800], [2,600], [3,400], [4,200], [5,0]]},
        {label: 'baz', data: [[1,100], [2,200], [3,300], [4,400], [5,500]]},
    ];
    '''    
#    mylist ='''[
#        {'label': 'foo', 'data': [[1,300], [2,300], [3,300], [4,300], [5,300]]},
#        {'label': 'bar', 'data': [[1,800], [2,600], [3,400], [4,200], [5,0]]},
#        {'label': 'baz', 'data': [[1,100], [2,200], [3,300], [4,400], [5,500]]},
#    ]'''    
    cursor = connection.cursor()
    
    #
    # WARNING - the 'char '%' is interpreted as a symbol for place holder.
    #     That is where we are getting the crazy error from.
    #
    sqlquery = '''SELECT rdetail.racedate, rresults.finalpos 
FROM (
    (rcdata_singleraceresults as rresults INNER JOIN rcdata_racerid as rid ON rresults.racerid_id = rid.id)
        INNER JOIN rcdata_singleracedetails as rdetail ON rdetail.id = rresults.raceid_id)        
WHERE (racerpreferredname ILIKE '%%anthony%%' AND 
       racerpreferredname ILIKE '%%honstain%%' AND
       rdetail.racelength = 8 AND
       rdetail.trackkey_id = 1 AND
       rdetail.racedata ILIKE '%%Mod Short Course A Main%%')
ORDER BY rdetail.racedate DESC
LIMIT 100;'''
    
    
    # Data retrieval operation - no commit required
    #cursor.execute("SELECT racerpreferredname FROM polls_racerid WHERE id = %s", ['1'])
    
    cursor.execute(sqlquery)
    results = cursor.fetchall()
    
    '''
    The timestamps must be specified as Javascript timestamps, as
      milliseconds since January 1, 1970 00:00. This is like Unix
      timestamps, but in milliseconds instead of seconds (remember to
      multiply with 1000!)
    '''
    graphdata = []
    for result in results:        
        # Convert to milliseconds
        formatedtime = time.mktime(result[0].timetuple()) * 1000        
        graphdata.append([formatedtime, result[1]])
                          
    print "GRAPHDATA", graphdata
    
    mylist =[
        {'label': 'Anthony Honstain', 'data': graphdata},        
    ]
    jsdata = simplejson.dumps(mylist)
    
    return render_to_response('myresults.html', {'jsdata':jsdata})
"""