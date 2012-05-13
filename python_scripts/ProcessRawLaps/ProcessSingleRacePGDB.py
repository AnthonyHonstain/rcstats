'''
Created on Apr 23, 2012

@author: Anthony Honstain


Overivew and reference for this module.
    The basic parts of raceData that we are interested in:
        
    self.date = None
    self.trackName = None
    self.raceClass = None
    self.roundNumber = None
    self.raceNumber = None

    self.raceHeaderData = [] # List of Dictionaries
    self.lapRowsTime = [] # List of Lists
    self.lapRowsPosition = []

    EXAMPLE OF SELECTING DATA FROM Database and working with it:
    cur = sql.cursor()
    cur.execute( "select * from rcdata_singleracedetails" )        
    results = cur.fetchall()
    print "="*40 + "\n" + "Printline debugging\n" + "="*40
    print "Current Description:\n\t" + str(cur.description)
    print "Results            :\n\t" + str(results)
    print "="*40
    cur.close()

    Current Description:
    [('id', 'int4', None, 4, None, None, None), 
    ('trackkey_id', 'int4', None, 4, None, None, None), 
    ('racedata', 'varchar', None, -1, None, None, None), 
    ('roundnumber', 'int4', None, 4, None, None, None), 
    ('racenumber', 'int4', None, 4, None, None, None), 
    ('racedate', 'timestamptz', None, 8, None, None, None), 
    ('uploaddate', 'timestamptz', None, 8, None, None, None)]
    Results            :
    []
  
'''

import pgdb
import time
import sys
import traceback
import logging



# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='ReadLaps.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logger1 = logging.getLogger('UploadToPostgres')


# Database table names
_trackName_tblname = "rcdata_trackname"
_trackName_column_trackname = "trackname"

_racerName_tblname = "rcdata_racerid"
_racerName_column_trackname = "racerpreferredname" 

_lapTimes_tablname = "rcdata_laptimes"

_raceDetails_tblname = "rcdata_singleracedetails"

_raceResults_tblname = "rcdata_singleraceresults"


def ProcessSingleRacePGDB(singleRaceData, database_name, user_name, passwd):
    # Get the SQL connection
    sql = pgdb.connect(database=database_name, 
                       user=user_name, 
                       password=passwd) #host='127.0.0.0', port=8080)
    """
    The following code will insert the singleRaceData into the database, it will use multiple
    select and inserts to ensure the information for the race is stored in the 
    appropriate tables.
    """
    
    try:
        trackName_selectcmd = "select * from " + _trackName_tblname +\
            " where " + _trackName_column_trackname +\
            " like '" + singleRaceData.trackName + "';"
              
        trackName_insertcmd = "insert into " + _trackName_tblname +\
            " values (nextval('" + _trackName_tblname + "_id_seq'), '" +\
            singleRaceData.trackName + "');"

        # I need to see if this is a known track, and if it is, grab the key
        # for the insert of the race data.
        trackKey = _insertRetrieveKey(sql, trackName_selectcmd, trackName_insertcmd)
        
        # For each racer, we need to insert them if they are not already.
        for headerDict in singleRaceData.raceHeaderData:
            
            racerName_selectcmd = "select * from " + _racerName_tblname +\
                " where " + _racerName_column_trackname +\
                " like '" + headerDict['Driver'] + "';"
            
            racerName_insertcmd = "insert into " + _racerName_tblname +\
                " values (nextval('" + _racerName_tblname + "_id_seq'), '" +\
                headerDict['Driver'] + "');"
        
            headerDict['racerKey'] = _insertRetrieveKey(sql, racerName_selectcmd, racerName_insertcmd)
            
        # We need to calculate the length of the race.
        racelength = _CalculateRaceLength(singleRaceData.raceHeaderData)

        winningLapCount = _CalculateWinningLaps(singleRaceData.raceHeaderData, singleRaceData.lapRowsTime)

        # Now that we know the track and the racers are in the database, insert the race.
        racedetailskey = _insert_singleRaceDetails(sql, 
                                                  trackKey, 
                                                  singleRaceData.raceClass, 
                                                  singleRaceData.roundNumber,
                                                  singleRaceData.raceNumber,
                                                  singleRaceData.date,
                                                  racelength,
                                                  winningLapCount)
    
        # Now we need to insert the lap data for each racer.
        #      lapRowsTime = [] # List of Lists
        _insertLapData(sql, 
                       singleRaceData.raceHeaderData, 
                       racedetailskey, 
                       singleRaceData.lapRowsTime, 
                       singleRaceData.lapRowsPosition)
        
        _insert_singleRaceResults(sql, racedetailskey, singleRaceData.raceHeaderData)
        
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        errortxt = "Failed to upload file: {0} raceClass: {1} exception: {2} {3}"
        logger1.error(errortxt.format(singleRaceData.filename, 
                                      singleRaceData.raceClass,
                                      str(e),
                                      trace))
    sql.close()


def _CalculateRaceLength(raceHeaderData):
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


def _CalculateWinningLaps(raceHeaderData, lapRowsTime):
    '''
    Calculate the winning number of laps.
    '''
    maxLaps = 0;
    for racer in raceHeaderData:
        if (racer['Laps'] > maxLaps):
            maxLaps = racer['Laps']
    
    # You can not be sure of this, it depends on how the scoring is set up, 
    # it is different depending on track.
    # Do an additional sanity check.
    #lapTimesCount = len(lapRowsTime[0]) - 1 # The first lap (partial) does not count.    
    #if (maxLaps != lapTimesCount):
    #    errortxt = "Unexpected winning number of laps in lapRowsTime, raceHeaderData: {0} lapRowsTime: {1}"
    #    logger1.error(errortxt.format(raceHeaderData, lapRowsTime))
        
    return maxLaps


def _insertLapData(sql, raceHeaderData, raceDetailskey, lapRowsTime, lapRowsPosition):
    """
    insert all of the laps for this race.
    """
    # For each racer in the raceHeaderData
    for racer in raceHeaderData:
        
        # Upload each lap
        index = racer['Car#'] - 1
        
        # This would be a good place to check and see if there are enough laps, it
        # has been observed that the parser can fail to get everyone's lap data (another
        # pending bug).
        
        for row in range(0, len(lapRowsTime[index])):
            # print "Debug: ", racer
            # print "Debug: ", lapRowsPosition[index]
            if (lapRowsPosition[index][row] == ''):
                lapRowsPosition[index][row] = 'null'
                lapRowsTime[index][row] = 'null'

            #  id | raceid_id | racerid_id | racelap | raceposition | racelaptime
            rawcmd = "insert into " + _lapTimes_tablname + " values ( " +\
                "nextval('" + _lapTimes_tablname + "_id_seq'), {0}, {1}, {2}, {3}, {4})"
            cmd = rawcmd.format(raceDetailskey, 
                                racer['racerKey'], 
                                row, 
                                lapRowsPosition[index][row],
                                lapRowsTime[index][row])
            # print "Debug: ", cmd
            cur = sql.cursor()
            cur.execute(cmd)  
            cur.close()
            sql.commit()


def _insertRetrieveKey(sql, selectcmd, insertcmd):
    """
    Generic method to attempt to select and retrieve the primary key for a db. It is
    expecting 
    """
    cur = sql.cursor()
    cur.execute(selectcmd)
    results = cur.fetchall()
    cur.close()
    '''
    # Logging
    print "="*40 + "\n" + "Logging - Try and retrieve the trackname.\n" + "-"*40
    #print "Current Description:\n\t" + str(cur.description)
    print "Results:\t" + str(results)
    print "="*40
    '''
    # We need to insert the track if it is not already present.
    if (len(results) < 1):
            cur = sql.cursor()
            cur.execute(insertcmd)  
            cur.close()
            sql.commit()
    else:
        return results[0][0]

    # Retrieve the key that was created during the insertion, and pass it back
    cur = sql.cursor()
    cur.execute(selectcmd)
    results = cur.fetchall()
    cur.close()
    
    logger1.debug("Processed new key:{0} insertcmd:{1}".format(results[0][0], insertcmd))

    '''
    # Logging
    print "="*40 + "\n" + "Logging - Retrieve the key for the track we inserted.\n" + "-"*40
    #print "Current Description:\n\t" + str(cur.description)
    print "Results:\t" + str(results)
    print "="*40
    '''
    return results[0][0]


def _insert_singleRaceDetails(sql, trackKey, className, roundNum, raceNum,  date, racelength, winninglapcount):
    # Logging first, since alot of problems can come from this insert.
    logger1.debug("Processing  racedetails className:{0} roundNum:{1} raceNum:{2} date:{3}".format(
            className, 
            roundNum,
            raceNum,
            date))
    """
    Overview of how to insert time from the format I parse from the raw text
    files, into the postgres time format.

     insert into rcdata_singleracedetails values (2, 'Stock Buggy Test', '2012-01-04 20:20:20-01')
    
     I have to find some way to change this date into something I can use.
     The raw version of what I have to work with.
         self.date: 10:32:24 PM  8/13/2011
    
     The general approach to creating a python time object.
        import time
        time.strptime("30 Nov 00", "%d %b %y")
    
     How to turn the time into a general python time object
        >>> timestrc = time.strptime("10:32:24 PM 8/13/2011", "%I:%M:%S %p %m/%d/%Y")
        >>> timestrc
        time.struct_time(tm_year=2011, tm_mon=8, tm_mday=13, tm_hour=22, 
                        tm_min=32, tm_sec=24, tm_wday=5, tm_yday=225, tm_isdst=-1)
    
     How to output the time in a new format.
vvv        strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        'Thu, 28 Jun 2001 14:17:15 +0000'
    
     HACK HACK HACK
        >>> time.strftime('%Y-%m-%d %H:%M:%S-01', timestrc)
        '2011-08-13 22:32:24-01'
    """
    # Parse this '10:32:24 PM  8/13/2011'
    timestruct = time.strptime(date, "%I:%M:%S %p %m/%d/%Y")
    
    # Format the time to get something like this '2012-01-04 20:20:20-01'
    formatedtime = time.strftime('%Y-%m-%d %H:%M:%S-01', timestruct)
    currenttime = time.strftime('%Y-%m-%d %H:%M:%S-01', time.localtime())

    # Befor we insert, we should see if this already exists in the database
    cur = sql.cursor()
    #id | trackkey_id |      racedata      | roundnumber | racenumber |        racedate        |       uploaddate       
    rawcmd = "SELECT * FROM " + _raceDetails_tblname +\
        " WHERE  trackkey_id = {0} AND racedata LIKE '{1}' " +\
        "AND roundnumber = {2} AND racenumber = {3} AND racedate = '{4}'"
    cmd = rawcmd.format(trackKey, className, roundNum, raceNum, formatedtime)
    cur.execute(cmd)
    results = cur.fetchall()
    cur.close()
    
    '''
    # Logging
    print "="*40 + "\n" + "Logging - Try and retrieve the singleracedetails.\n" + "-"*40
    #print "Current Description:\n\t" + str(cur.description)
    print "Results:\t" + str(results)
    print "="*40
    '''
    # We need to insert the track if it is not already present.
    if (len(results) > 0):
        logger1.error("The race has already been processed into the DB")
        raise Exception("The race has already been processed into the DB")

    cur = sql.cursor()
    rawcmd = "insert into " + _raceDetails_tblname + " values " +\
        "( nextval('" + _raceDetails_tblname + "_id_seq'), " +\
        "{0}, '{1}', {2}, {3}, '{4}', '{5}', {6}, {7})"
        
    cmd = rawcmd.format(trackKey, 
                        className, 
                        roundNum, 
                        raceNum, 
                        formatedtime, 
                        currenttime,
                        racelength,
                        winninglapcount)
    cur.execute(cmd)    
    cur.close()
    sql.commit()
    
    
    cur = sql.cursor()
    #id | trackkey_id |      racedata      | roundnumber | racenumber |        racedate        |       uploaddate       
    rawcmd = "SELECT id FROM " + _raceDetails_tblname + " WHERE " +\
        " trackkey_id = {0} AND racedata LIKE '{1}' AND roundnumber = {2} " +\
        " AND racenumber = {3} AND racedate = '{4}'"
    
    cmd = rawcmd.format(trackKey, className, roundNum, raceNum, formatedtime)
    cur.execute(cmd)
    results = cur.fetchall()
    cur.close()    
    return results[0][0]


def _insert_singleRaceResults(sql, raceDetailsKey, raceHeaderData):
       
    '''
    Warning - to fields to be concerned about -
        'RaceTime' - Because it may have '0.000'
        'Fast Lap' - Because it may be blank.
            _________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
            John Doe            #1          0            0.000
        'Behind' - Because it may not exist.
        
    Example of the data structure we will work with here:
                          [{"Driver":"TOM WAGGONER", 
                          "Car#":"9", 
                          "Laps":"26", 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":9} , ...]
    '''
    # We are assuming that the check to see if this race was already inserted was
    # done already (when the raceDetailsKey was retrieved).
    cur = sql.cursor()
    
    #rcraceperformance=> select * from rcdata_singleraceresults;
    #id | raceid_id | racerid_id | carnum | lapcount | racetime | fastlap | behind | finalpos 

    insert = "INSERT INTO " + _raceResults_tblname +\
        " (id, raceid_id, racerid_id, carnum, lapcount, " +\
        "racetime, fastlap, behind, finalpos) " +\
        "VALUES ( " +\
        "nextval('" + _raceResults_tblname + "_id_seq'), " +\
        "%(raceid_id)s, " +\
        "%(racerid_id)s, " +\
        "%(carnum)s, " +\
        "%(lapcount)s, " +\
        "%(racetime)s, " +\
        "%(fastlap)s, " +\
        "%(behind)s, " +\
        "%(finalpos)s);"
        
    params = []
    # For each racer in the raceHeaderData
    for racer in raceHeaderData:
        if (racer['RaceTime'] == ''):
            racer['RaceTime'] = None
        if (racer['Fast Lap'] == ''):
            racer['Fast Lap'] = None
        if (racer['Behind'] == ''):
            racer['Behind'] = None
           
        params.append({ 'raceid_id': raceDetailsKey, 
                        'racerid_id': racer['racerKey'],
                        'carnum': racer['Car#'], 
                        'lapcount': racer['Laps'], 
                        'racetime': racer['RaceTime'],
                        'fastlap': racer['Fast Lap'],
                        'behind': racer['Behind'],
                        'finalpos': racer['Final Position']})
        
    cur.executemany(insert, params)
    cur.close()
    sql.commit()

