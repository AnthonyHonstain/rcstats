from django.views.decorators.cache import cache_page

from django.shortcuts import render_to_response
from django.template import RequestContext

@cache_page(60 * 60 * 12)
def index(request):
    
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

@cache_page(60 * 60 * 12)
def faq(request):
    
    return render_to_response('faq.html', {}, context_instance=RequestContext(request))
