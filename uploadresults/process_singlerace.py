from rcstats.rcdata.database_cleanup import collapse_alias_classnames, collapse_racer_names

from rcstats.rcdata.models import TrackName
from rcstats.rcdata.models import RacerId
from rcstats.rcdata.models import SingleRaceDetails
from rcstats.rcdata.models import SingleRaceResults
from rcstats.rcdata.models import LapTimes

import time
import datetime


def process_singlerace(race):
    '''
    Insert the information in the singlerace object into the DB.
    
    Conditions - The trackname is already in the db.
    '''
    
    # ====================================================
    # Trackname
    # ====================================================
    # Track - We assume it has already been validated that this is a known track.
    #    NOTE - we do not want to be creating new tracks in this code, if the track
    #    is new it probably means they are not uploading appropriately.
    track_obj = TrackName.objects.get(trackname=race.trackName)
            
    # ====================================================
    # Insert Racers
    # ====================================================
    # We want to add a new racerid if one does not already exist.
    for racer in race.raceHeaderData:
        racer_obj, created = RacerId.objects.get_or_create(racerpreferredname=racer['Driver'])
        racer['racer_obj'] = racer_obj
        
    # ====================================================
    # Insert Race Details
    # ====================================================
    # Find race length
    racelength = _calculate_race_length(race.raceHeaderData)
    
    # Find Winning lap count
    maxlaps = 0;
    for racer in race.raceHeaderData:
        if (racer['Laps'] > maxlaps):
            maxlaps = racer['Laps']
      
    # Parse this '10:32:24 PM  8/13/2011'
    timestruct = time.strptime(race.date, "%I:%M:%S %p %m/%d/%Y")    
    # Format the time to get something like this '2012-01-04 20:20:20-01'
    formatedtime = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
    currenttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    # We want to stop if this race is already in the database
    
    test_objs = SingleRaceDetails.objects.filter(trackkey=track_obj,
                                            racedata=race.raceClass,    
                                            roundnumber=race.roundNumber,
                                            racenumber=race.raceNumber,
                                            racedate=formatedtime,
                                            racelength=racelength,
                                            winninglapcount=maxlaps,
                                            mainevent=race.mainEvent, 
                                            maineventroundnum=race.mainEventRoundNum, 
                                            maineventparsed=race.mainEventParsed)
        
    if (len(test_objs) != 0):    
        # We want to tell the user since this not what they wanted.
        # We can be reasonably certain this file has already been uploaded.
        raise FileAlreadyUploadedError(race, "File already uploaded")
        
    details_obj = SingleRaceDetails(trackkey=track_obj,
                                    racedata=race.raceClass,
                                    roundnumber=race.roundNumber,
                                    racenumber=race.raceNumber,
                                    racedate=formatedtime,
                                    uploaddate=currenttime,
                                    racelength=racelength,
                                    winninglapcount=maxlaps,
                                    mainevent=race.mainEvent, 
                                    maineventroundnum=race.mainEventRoundNum, 
                                    maineventparsed=race.mainEventParsed)
    details_obj.save()
    
    # ====================================================
    # Insert Race Laps
    # ====================================================    
    # For each racer in the raceHeaderData
    for racer in race.raceHeaderData:        
        # Upload each lap for this racer, their care number - 1 indicates
        # the index of their laps in the lapRowsTime list.
        index = racer['Car#'] - 1
        
        # This would be a good place to check and see if there are enough laps, it
        # has been observed that the parser can fail to get everyone's lap data (another
        # pending bug).        
        for row in range(0, len(race.lapRowsTime[index])):
            # print "Debug: ", racer
            # print "Debug: ", lapRowsPosition[index]
            if (race.lapRowsPosition[index][row] == ''):
                race.lapRowsPosition[index][row] = None
                race.lapRowsTime[index][row] = None

            lap_obj = LapTimes(raceid=details_obj, 
                               racerid=racer['racer_obj'], 
                               racelap=row, 
                               raceposition=race.lapRowsPosition[index][row],
                               racelaptime=race.lapRowsTime[index][row])
            lap_obj.save()
            
    # ====================================================
    # Insert Race Results
    # ====================================================
    '''
        Example of the data structure we will work with here:
                          [{"Driver":"TOM WAGGONER", 
                          "Car#":"9", 
                          "Laps":"26", 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":9} , ...]
    '''
    for racer in race.raceHeaderData:
        if (racer['RaceTime'] == ''):
            racer['RaceTime'] = None
        else:
            # Convert the racetime to a datetime.time object,
            # this is required to ensure the microseconds are not
            # chopped off.
            racer['RaceTime'] = datetime.datetime.strptime(racer['RaceTime'], "%M:%S.%f")
            
        if (racer['Fast Lap'] == ''):
            racer['Fast Lap'] = None
        if (racer['Behind'] == ''):
            racer['Behind'] = None
           
        individual_result = SingleRaceResults(raceid=details_obj, 
                                              racerid=racer['racer_obj'],
                                              carnum=racer['Car#'], 
                                              lapcount=racer['Laps'], 
                                              racetime=racer['RaceTime'],
                                              fastlap=racer['Fast Lap'],
                                              behind=racer['Behind'],
                                              finalpos=racer['Final Position'])
        individual_result.save()       

    # TODO - I can see the following code being good stuff to log.    
    
    # ===============================================================
    # Collapse alias racer names.
    # ===============================================================
    collapse_racer_names()
    
    # ===============================================================
    # Collapse class names.
    # ===============================================================    
    # Note - this likely changed the race's name.
    collapse_alias_classnames(SingleRaceDetails.objects.filter(id__exact=details_obj.id))

    return details_obj


def _calculate_race_length(raceHeaderData):
    '''
    Look at all the racetimes and take largest number of minutes (note: we only
    look at the number of minutes in the race, not the number of seconds).
    
    Some people may be recorded as not going the entire race time, or have no
    race time at all.
    '''
    maxNumMinutes = 0
    
    for racer in raceHeaderData:
        if (racer["RaceTime"] == ''):
            continue
        else:
            numMin = int(racer["RaceTime"].split(':')[0])
            if numMin > maxNumMinutes:
                maxNumMinutes = numMin
    
    return maxNumMinutes


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class FileAlreadyUploadedError(Error):
    """Exception raised when a race has already been placed in the system..

    Attributes:
        singlerace -- singlerace object that was being processed.
    """

    def __init__(self, singlerace, msg):
        self.singlerace = singlerace
        self.msg = msg
        