'''
Created on Oct 18, 2012

@author: Anthony Honstain

I am going to push the class and main event data to new columns. Prior to this change
I need to repeat the calculation on the string for the class name "Mod Buggy A-main" 
(by running a regex against it), I had to do this in several places (from ranking to
displaying track data).

After running this script, I will be able to query against main events, and I will
have a single place to modify (uploader) if want to add new ways of identifying 
main events. 

This migration script will serve as the jumping off point for when I modify
the uploader. (This is a phased upgrade).
1 - Add new columns and populate them
2 - Migrate code to using the new columns
3 - Remove the main event data from the origional race data column
4 - Change the racedata column name to classname
'''

from optparse import OptionParser
import pgdb
import re
            
def main():
    parser = OptionParser()

    parser.add_option("-d", "--database", dest="database",
                      help="database name")

    parser.add_option("-u", "--username", dest="username",
                      help="User name for database")

    parser.add_option("-p", "--password", dest="password",
                      help="Password for database")
    
    parser.add_option("-m", '--modify_racedata', dest="modify_racedata", action="store_true",
                      help="Modify the racedata column to remove main event info")

    (options, args) = parser.parse_args()

    # Get the SQL connection
    sql = pgdb.connect(database=options.database, 
                       user=options.username,
                       password=options.password) #host='127.0.0.0', port=8080)

    
    modify_racedata = options.modify_racedata
    
    _race_details_tblname = "rcdata_singleracedetails"
  
    # First step is to get all the race details.
    cur = sql.cursor()
    get_racedetails = "SELECT id, racedata FROM " + _race_details_tblname + ";"
    cur.execute(get_racedetails)
    results = cur.fetchall()
    cur.close()    
    # Example results:
    #   [3289, 'Mod Buggy A Main']
    #   [3290, 'Stock Buggy A Main']

    
    if (len(results) < 1):
        raise Exception("No results were returned from the database.")
    
    # Business logic - I have to assume a basic format, if someone
    # comes up with some crazy format like "AAA main", I will
    # build a seperate case/check for it.
    
    # The white space in the regex means we avoid error checking below.
    pattern = re.compile("[A-Z][1-9]? main", re.IGNORECASE)
    
    for race_detail in results:
        match = pattern.search(race_detail[1])
        if not match:
            # Nothing to do if we don't spot a main event.
            print 'Ignoring:', race_detail
            continue
        
        start_index = match.start(0)
    
        # Fields we want to parse out
        cleaned_raceclass_name = ""
        main_event = None # Indicates A,B,C, etc main event
        main_event_round_number = None # Indicates the round for multiple main events A1, C2, etc.
        
        
        # We want to trim off the 'A main' part of the string and clean it up.
        cleaned_raceclass_name = race_detail[1][:start_index]
        # I added an additional cleanup, since I saw some older results with extra
        # junk characters in the name.
        cleaned_raceclass_name = cleaned_raceclass_name.strip('+- ')
        
        main_event_raw = race_detail[1][start_index:].strip('+- ')    

        # The regex means there must be a white space here.        
        main_event_round_raw = main_event_raw.split()[0]
        
        main_event = _convert_mainevent(main_event_round_raw[0].upper())
            
        if len(main_event_round_raw) > 1:
            # We are looking for the case like: "A1", "A3"
            # I have left it open to the possibility of multiple B,C, etc.
            main_event_round_number = int(main_event_round_raw[1:])
                
        print 'raceclass:{0:25} mainevent:{1} maineventroundnumber:{2:5} Orig:{3} '.format(cleaned_raceclass_name, main_event, main_event_round_number, race_detail)
        
        # ------------------------------------
        # Update the race results
        # ------------------------------------
        cur = sql.cursor()
        insert = "UPDATE " + _race_details_tblname +\
                 " SET mainevent = %(mainevent)s ," +\
                 "     maineventroundnum = %(maineventroundnum)s ," +\
                 "     maineventparsed = %(maineventparsed)s" +\
                 " WHERE  id = %(id)s ;"
        
        params = []
        #for alias in alias_list:                       
        params.append({'id': race_detail[0],
                           'mainevent': main_event,
                           'maineventroundnum':main_event_round_number,
                           'maineventparsed': main_event_raw,
                           })
                
        cur.executemany(insert, params)
        cur.close()
        sql.commit()

        # ---------------------------------------
        # This is for the final step, after we have fixed
        # the rest of the code. REMOVE main event info
        # from the racedata column.
        # ---------------------------------------
        if modify_racedata:
            cur = sql.cursor()
            insert = "UPDATE " + _race_details_tblname +\
                     " SET racedata = %(racedata)s ," +\
                     "     mainevent = %(mainevent)s ," +\
                     "     maineventroundnum = %(maineventroundnum)s ," +\
                     "     maineventparsed = %(maineventparsed)s" +\
                     " WHERE  id = %(id)s ;"
            
            params = []
            #for alias in alias_list:                       
            params.append({'id': race_detail[0], 
                               'racedata': cleaned_raceclass_name,
                               'mainevent': main_event,
                               'maineventroundnum':main_event_round_number,
                               'maineventparsed': main_event_raw,
                               })
                    
            cur.executemany(insert, params)
            cur.close()
            sql.commit()


def _convert_mainevent(event_char):
    # "A" -> 65
    return ord(event_char) - 64

if __name__ == '__main__':
    main()
    