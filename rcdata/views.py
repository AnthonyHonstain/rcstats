import time
import datetime
from dateutil.relativedelta import relativedelta

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
#from polls.models import Poll
from django.http import HttpResponse, Http404

from django.db import connection

from django.utils import simplejson

from rcdata.models import SupportedTrackName

# *********************************************
# The old index, awating redesign.
# *********************************************
#def index(request):
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
#    t = loader.get_template('polls/index.html')
#    c = Context({
#        'latest_poll_list': latest_poll_list,
#    })
    
#    return HttpResponse(t.render(c))

# Use the template to provide more detail than just a simple string response.
def index(request):
    #p = get_object_or_404(Poll, pk=poll_id)
    
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
    # WARNING - the 'char '%' is interpreted as a symbold for place holder.
    #     That is where we are getting the crazy error from.
    #
    sqlquery = '''SELECT rdetail.racedate, rresults.finalpos 
FROM (
    (rcdata_singleraceresults as rresults INNER JOIN rcdata_racerid as rid ON rresults.racerid_id = rid.id)
        INNER JOIN rcdata_singleracedetails as rdetail ON rdetail.id = rresults.raceid_id)        
WHERE (racerpreferredname ILIKE '%%george%%' AND 
       racerpreferredname ILIKE '%%cherry%%' AND
       rdetail.racelength = 8 AND
       rdetail.trackkey_id = 2 AND
       rdetail.racedata ILIKE '%%Modified BUGGY A Main%%')
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
        {'label': 'George Cherry', 'data': graphdata},        
    ]
    jsdata = simplejson.dumps(mylist)
    
    return render_to_response('index.html', {'jsdata':jsdata})

def trackdata(request):
    tracklist = SupportedTrackName.objects.all()

    return render_to_response('trackdata.html', {'track_list':tracklist})

def trackdetail(request, track_id, time_frame='alltime'):
    p = get_object_or_404(SupportedTrackName, pk=track_id)
    
    if (time_frame not in ('alltime', 'month', '6months')):
        raise Http404
    
    sqltimefilter = ''
    filterdatestr = 'All Time'
    if (time_frame == 'month'):
        filterdate = datetime.datetime.now() + relativedelta(months=-1)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sqltimefilter = "AND rdetails.racedate > '" + dbdate + "'"
    elif (time_frame == '6months'):
        filterdate = datetime.datetime.now() + relativedelta(months=-6)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sqltimefilter = "AND rdetails.racedate > '" + dbdate + "'"
    
    cursor = connection.cursor()
    sqlquery = '''SELECT racedata.id, racedata.racerpreferredname, SUM(racedata.finalpos) FROM
      (
      SELECT rresults.raceid_id, racerids.id, racerids.racerpreferredname, rresults.finalpos FROM
          /* Get all the racer ids */
          (SELECT id, racerpreferredname FROM rcdata_racerid as rid 
           ) as racerids,
        /* Get all the races those racerids were in */
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = racerids.id AND
            rresults.finalpos = 1    
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sqltimefilter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.id, racedata.racerpreferredname
    ORDER BY SUM(racedata.finalpos) desc
    LIMIT 30;'''
       
    cursor.execute(sqlquery, {'trackkey':p.trackkey.id})
    topwins = cursor.fetchall()

    querytoplaps = '''SELECT racedata.id, racedata.racerpreferredname, SUM(racedata.lapcount) FROM
      (
      SELECT rresults.raceid_id, racerids.id, racerids.racerpreferredname, rresults.lapcount FROM
          /* Get all the racer ids */
          (SELECT id, racerpreferredname FROM rcdata_racerid as rid 
           ) as racerids,
        /* Get all the races those racerids were in */
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = racerids.id
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sqltimefilter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.id, racedata.racerpreferredname
    ORDER BY SUM(racedata.lapcount) desc
    LIMIT 30;'''
       
    cursor.execute(querytoplaps, {'trackkey':p.trackkey.id})
    toplaps = cursor.fetchall()
        
    ctx = Context({'trackname':p.trackkey,
                   'filterdate':filterdatestr,
                   'topwins':topwins, 
                   'toplaps':toplaps})
    return render_to_response('trackdatadetail.html', ctx)
    


#def detail(request, poll_id):
#    return HttpResponse("You're looking at poll %s." % poll_id)

#def results(request, poll_id):
#    return HttpResponse("You're looking at the results of poll %s." % poll_id)
#
#def vote(request, poll_id):
#    return HttpResponse("You're voting on poll %s." % poll_id)
