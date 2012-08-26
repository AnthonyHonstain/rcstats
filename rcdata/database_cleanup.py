'''
Created on Aug 24, 2012

@author: Anthony Honstain

This is collection of higher level scripts for administrator or key section of code
to process or cleanup data in the database.

'''

from rcstats.rcdata.models import SingleRaceDetails, RacerId, TrackName
from rcstats.rcdata.models import SupportedTrackName, OfficialClassNames, AliasClassNames

import re


def collapse_alias_classnames(queryset):
    '''
    collapse_alias_classnames takes a queryset of SingleRaceDetails and will use
    the mapping between OfficialClassNames and AliasClassNames to clean up
    the classnames.
    
    This means setting the correct case on the class name if it is different from the official.
    This means changing an alias to the offical class name if they differ.
    '''
    
    # First we need to construct an efficient structure for checking
    
    # Note - all the of the keys in lookup and offical_classnames are LOWERCASE
    lookup = {}
    official_classnames = {} # This is where the official names (unmodified case) are stored.
    
    officalclass_queryset = OfficialClassNames.objects.all()
    for officialclass in officalclass_queryset:
        lookup[officialclass.raceclass.lower()] = None
        official_classnames[officialclass.raceclass.lower()] = officialclass.raceclass
    
    alliasclass_queryset = AliasClassNames.objects.all()
    for alliasclass in alliasclass_queryset:
        lookup[alliasclass.raceclass.lower()] = alliasclass.officialclass.raceclass
    
    pattern = re.compile("[A-Z][1-9]?.main", re.IGNORECASE)
    for racedetail in queryset:
        raceclass = racedetail.racedata
                
        start_index = None
        main = ""
        if (pattern.search(raceclass) != None):
            start_index = pattern.search(raceclass).start(0)
            raceclass = raceclass[:start_index].strip('+- ')
            main = " " + racedetail.racedata[start_index:]
        
        if raceclass.lower() in lookup:
            #print "HIT:", raceclass.lower(), racedetail.racedata
            
            # We found a hit, this is either an official class, or we will change it.
            if (lookup[raceclass.lower()] == None):
                # This is an official class, we just need to check if case is good.
                if (official_classnames[raceclass.lower()] != raceclass[:start_index]):
                    # The class is named correctly, but we are going to fix the case.
                    racedetail.racedata = official_classnames[raceclass.lower()] + main 
                    #print "CASE FIXED:", racedetail.racedata
                    racedetail.save()                
            else:
                # We need to set this to the official class name.
                racedetail.racedata = lookup[raceclass.lower()] + main
                #print "ALIAS FIXED:", racedetail.racedata
                racedetail.save()