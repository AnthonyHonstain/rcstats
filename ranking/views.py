from django.shortcuts import render_to_response
from django.template import RequestContext

def ranking(request):
    
    return render_to_response('ranking.html', {}, context_instance=RequestContext(request))
