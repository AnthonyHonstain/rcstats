import os
import sys

path = '/home/asymptote/Desktop/rcstats_pydev/rcstats'
if path not in sys.path:
   sys.path.append(path)
path = '/home/asymptote/Desktop/rcstats_pydev'
if path not in sys.path:
   sys.path.append(path)


os.environ['DJANGO_SETTINGS_MODULE'] = 'rcstats.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

