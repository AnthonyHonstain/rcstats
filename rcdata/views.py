import time

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
#from polls.models import Poll
from django.http import HttpResponse

from django.db import connection

from django.utils import simplejson

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
#def detail(request, poll_id):
#    return HttpResponse("You're looking at poll %s." % poll_id)

#def results(request, poll_id):
#    return HttpResponse("You're looking at the results of poll %s." % poll_id)
#
#def vote(request, poll_id):
#    return HttpResponse("You're voting on poll %s." % poll_id)
