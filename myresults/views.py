import time
import datetime

from dateutil.relativedelta import relativedelta

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.db import connection
from django.utils import simplejson

from rcdata.models import RacerId, SupportedTrackName, SingleRaceDetails, SingleRaceResults


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

    mylist =[
        {'label': racer_obj.racerpreferredname, 'data': graphdata},        
    ]
    jsdata = simplejson.dumps(mylist)
        
            
    # -----------------------------------------------------------
    # Identify and group the race classes
    # -----------------------------------------------------------
    
    # WARNING - PROTOTYPE CODE    
    for result in race_results:
        race_detail = SingleRaceDetails.objects.get(pk = result.raceid.id)
        print race_detail.racedate, race_detail.racedata
        
    # Not sure if a static table is going to
    synonymes = {'mpd': ['mod', 'modified'],
                 'stock': ['stock', '17.5',],
                 'sc': ['short course', 'sc', ],
                 'truck':['truck', 'stadium']
                }
        
        
    ctx = Context({'racername':racer_obj.racerpreferredname, 'jsdata':jsdata})
    return render_to_response('generalstats.html', ctx)




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