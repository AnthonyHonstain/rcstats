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
    cur.execute( "select * from polls_singleracedetails" )        
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

import SingleRace
import pgdb
import time
import sys
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



def ProcessSingleRacePGDB(singleRaceData, database, user, password):
    # Get the SQL connection
    sql = _connectSqlWithPGDB(database, user, password)
    

    """
    The following code will insert the singleRaceData into the database, it will use multiple
    select and inserts to ensure the information for the race is stored in the 
    appropriate tables.
    """

    try:
        trackName_dbname = "polls_trackname"
        trackName_column_trackname = "trackname"

        trackName_selectcmd = "select * from " + trackName_dbname + " where " + trackName_column_trackname + " like '" + singleRaceData.trackName + "';"
        trackName_insertcmd = "insert into " + trackName_dbname + " values (nextval('" + trackName_dbname + "_id_seq'), '" + singleRaceData.trackName + "');"

        # I need to see if this is a known track, and if it is, grab the key
        # for the insert of the race data.
        trackKey = _insertRetrieveKey(sql, trackName_selectcmd, trackName_insertcmd)
        logger1.debug("Processed trackName:{0} trackKey:{1}".format(singleRaceData.trackName, trackKey))

        racerName_dbname = "polls_racerid"
        racerName_column_trackname = "racerpreferredname"
      
        # For each racer, we need to insert them if they are not already.
        for headerDict in singleRaceData.raceHeaderData:
            racerName_selectcmd = "select * from " + racerName_dbname + " where " + racerName_column_trackname + " like '" + headerDict['Driver'] + "';"
            racerName_insertcmd = "insert into " + racerName_dbname + " values (nextval('" + racerName_dbname + "_id_seq'), '" + headerDict['Driver'] + "');"
        
            headerDict['racerKey'] = _insertRetrieveKey(sql, racerName_selectcmd, racerName_insertcmd)
            #print "debugging - racerKey:", headerDict['racerKey']
            logger1.debug("Processed racer:{0} raceKey:{1}".format(headerDict['Driver'], headerDict['racerKey']))

        # Now that we know the track and the racers are in the database, insert the race.
        racedetailskey = _insert_singleRaceDetails(sql, 
                                                  trackKey, 
                                                  singleRaceData.raceClass, 
                                                  singleRaceData.roundNumber,
                                                  singleRaceData.raceNumber,
                                                  singleRaceData.date)
    
        # Now we need to insert the lap data for each racer.
        #    self.lapRowsTime = [] # List of Lists
        #    self.lapRowsPosition = []
        _insertLapData(sql, singleRaceData.raceHeaderData, racedetailskey, singleRaceData.lapRowsTime, singleRaceData.lapRowsPosition)

    except Exception:
        logger1.error("Failed to upload file: {0} raceClass: {1}".format(singleRaceData.filename, singleRaceData.raceClass))
    sql.close()


def _connectSqlWithPGDB(databse, user, password):
    """
    Opens the necessary connection to postgresql and returns the pgdb object. 
    """        
    # Does not look like I need the host or port.
    sql = pgdb.connect(database='django_lapTracker', 
                     user='asymptote', 
                     password='perrin25') #host='127.0.0.0', port=8080)

    #print "PrintLineDebug - sql: " + str(sql)    
    return sql


def _insertLapData(sql, raceHeaderData, raceDetailskey, lapRowsTime, lapRowsPosition):
    """
    insert all of the laps for this race.
    """
    # For each racer in the raceHeaderData
    for racer in raceHeaderData:
        
        # Upload each lap
        index = int(racer['Car#']) - 1
        
        for row in range(0, len(lapRowsTime[index])):
            # print "Debug: ", racer
            # print "Debug: ", lapRowsPosition[index]
            if (lapRowsPosition[index][row] == ''):
                lapRowsPosition[index][row] = 'null'
                lapRowsTime[index][row] = 'null'

            #  id | raceid_id | racerid_id | racelap | raceposition | racelaptime
            rawcmd = "insert into polls_singleracerdata values " +\
                "( nextval('polls_singleracerdata_id_seq'), {0}, {1}, {2}, {3}, {4})"
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
    
    '''
    # Logging
    print "="*40 + "\n" + "Logging - Retrieve the key for the track we inserted.\n" + "-"*40
    #print "Current Description:\n\t" + str(cur.description)
    print "Results:\t" + str(results)
    print "="*40
    '''
    return results[0][0]


def _insert_singleRaceDetails(sql, trackKey, className, roundNum, raceNum,  date):

    logger1.debug("Processing  racedetails className:{0} roundNum:{1} raceNum:{2} date:{3}".format(
            className, 
            roundNum,
            raceNum,
            date))
    """
    Overview of how to insert time from the format I parse from the raw text
    files, into the postgres time format.

     insert into polls_singleracedetails values (2, 'Stock Buggy Test', '2012-01-04 20:20:20-01')
    
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
    rawcmd = "SELECT * FROM polls_singleracedetails WHERE " +\
        " trackkey_id = {0} AND racedata LIKE '{1}' AND roundnumber = {2} AND racenumber = {3} AND racedate = '{4}'"
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
    rawcmd = "insert into polls_singleracedetails values " +\
        "( nextval('polls_singleracedetails_id_seq'), {0}, '{1}', {2}, {3}, '{4}', '{5}')"
    cmd = rawcmd.format(trackKey, className, roundNum, raceNum, formatedtime, currenttime)
    cur.execute(cmd)    
    cur.close()
    sql.commit()
    

    cur = sql.cursor()
    #id | trackkey_id |      racedata      | roundnumber | racenumber |        racedate        |       uploaddate       
    rawcmd = "SELECT id FROM polls_singleracedetails WHERE " +\
        " trackkey_id = {0} AND racedata LIKE '{1}' AND roundnumber = {2} AND racenumber = {3} AND racedate = '{4}'"
    cmd = rawcmd.format(trackKey, className, roundNum, raceNum, formatedtime)
    cur.execute(cmd)
    results = cur.fetchall()
    cur.close()    
    return results[0][0]


    
   


