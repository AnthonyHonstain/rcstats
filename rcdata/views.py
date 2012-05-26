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


def index(request):
    
    return render_to_response('index.html')

