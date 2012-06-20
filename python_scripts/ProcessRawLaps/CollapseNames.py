'''
Created on Jun 18, 2012

@author: Anthony Honstain

I have a number of different racer names, and many of them represent
the same person but have slightly different spelling, structure, letter case.

For the time being I need a quick and easy way to push these to a single name, so
that people can get their data in a single place.

'''

from optparse import OptionParser
import pgdb


class ProcessRacerId():


    def __init__(self, racerid_data):
               
        # This will contain the primary names that all others will be aliases of.
        # This should be the name which is most frequently raced under.
        self._primaryName_dict = {} 
        
        # I need to start identifying duplicates, there are several of the
        # most obvious reasons:
        #     Character Case - upper/lower
        #     FName - LName order
        #
        # I can save myself allot of grief if I assume names with more races should be the 
        # original, so that when I run this in the future, I am less likely to have updates.
        #for result in results:
        #    print result

        for result in racerid_data:            
            # We need to calculate the formated name (no case, reverse ordering of fname/lname).
            tempname = result[1].lower()
            
            comma_index = tempname.find(',')
            if (comma_index > -1):
                # This probably contains a name of the format "<lname>, <fname>"
                fname = tempname[comma_index + 1:].strip() 
                lname = tempname[0 : comma_index].strip()
                tempname = fname + " " + lname

            #print result
            #print '\t' + tempname
            
            # Now with the name formated, we can see it belongs in the dictionary
            if (not self._primaryName_dict.has_key(tempname)):
                
                # Before we add this as a new key, we are going to check if there
                # are any similarly spelled names.
                actual_spelling = self._check_edit_distance(tempname)
                
                # if _check_edit_distance found a key, that is the key will will
                # put this name under.
                if (actual_spelling != ""):
                    self._primaryName_dict[actual_spelling].append(result)
                else:
                    self._primaryName_dict[tempname] = [result]
                    
            else:
                # This means it was an unkown name with no aliases found.
                self._primaryName_dict[tempname].append(result)
            
        self.likely_aliases = filter(lambda x: len(x[1]) > 1, self._primaryName_dict.items())
            
        #print "Prining all the likely_aliases"
        #for key in likely_aliases:
        #    print '\t', key
      
      
    def _check_edit_distance(self, tempname):      
        for key in self._primaryName_dict.keys():
            if (len(key) == len(tempname) and +\
                self._misspell_count(key, tempname) == len(key) - 1):
                return key
        return ""
        
    def _misspell_count(self, origional_str, test_str):
        same_count = 0
        for i in range(min(len(origional_str), len(test_str))):
            if (origional_str[i] == test_str[i]):
                same_count += 1
        return same_count
            
def main():
    parser = OptionParser()

    parser.add_option("-d", "--database", dest="database",
                      help="database name")

    parser.add_option("-u", "--username", dest="username",
                      help="User name for database")

    parser.add_option("-p", "--password", dest="password",
                      help="Password for database")

    (options, args) = parser.parse_args()

    # Get the SQL connection
    sql = pgdb.connect(database=options.database, 
                       user=options.username,
                       password=options.password) #host='127.0.0.0', port=8080)

    
    _sql = sql 
    _racerName_tblname = "rcdata_racerid"
    _raceResult_tblname = "rcdata_singleraceresults"
    _laptimes_tblname = "rcdata_laptimes"
    
    # First step is to get all the racer names and their ids.               
    cur = sql.cursor()
    #get_racers_cmd = "SELECT * FROM " + _racerName_tblname + ";"
    get_racers_cmd = '''
        SELECT racerid.id, racerid.racerpreferredname, COUNT(rresult.id) 
        FROM ''' + _racerName_tblname + ''' as racerid , 
            '''+ _raceResult_tblname + ''' as rresult 
        WHERE racerid.id = rresult.racerid_id 
        GROUP BY racerid.id 
        ORDER BY COUNT(rresult.id) desc;
        '''
    cur.execute(get_racers_cmd)
    # Example results
    # [ [1, 'hovarter,kevin', 5], [2, 'gripentrog, kurt', 5], [3, 'Collins, Brandon', 2]
    
    results = cur.fetchall()
    cur.close()    
    
    if (len(results) < 1):
        raise Exception("No results were returned from the database.")
    
    processRacerObj = ProcessRacerId(results)


    for canidate in processRacerObj.likely_aliases:
        
        
        primary_name = canidate[1][0]
        alias_list = canidate[1][1:]
        print
        print "Primary:", primary_name
        print "Lkely Alias:", alias_list
        var = raw_input("\tEnter ANY character to collapse to primary: ")
        if (len(var) > 0):
            print 'COLLAPSING IN SQL'
            # ------------------------------------
            # Update the race results
            # ------------------------------------
            cur = sql.cursor()
            insert = "UPDATE " + _raceResult_tblname +\
                    " SET racerid_id = %(new_racerid)s " +\
                    " WHERE  racerid_id = %(old_racerid)s ;"
            
            params = []
            for alias in alias_list:                       
                params.append({'new_racerid': primary_name[0], 
                               'old_racerid': alias[0],
                               })
                    
            cur.executemany(insert, params)
            cur.close()
            sql.commit()
            
            # ------------------------------------
            # Update the lap times
            # ------------------------------------ 
            cur = sql.cursor()
            insert = "UPDATE " + _laptimes_tblname +\
                    " SET racerid_id = %(new_racerid)s " +\
                    " WHERE  racerid_id = %(old_racerid)s ;"
            
            params = []
            for alias in alias_list:                       
                params.append({'new_racerid': primary_name[0], 
                               'old_racerid': alias[0],
                               })
                    
            cur.executemany(insert, params)
            cur.close()
            sql.commit()
            
            # ------------------------------------
            # Remove the racerid
            # ------------------------------------
            cur = sql.cursor()
            insert = "DELETE FROM " + _racerName_tblname +\
                     " WHERE  id = %(old_racerid)s;"
            
            params = []
            for alias in alias_list:                       
                params.append({'old_racerid': alias[0],
                               })
                    
            cur.executemany(insert, params)
            cur.close()
            sql.commit()
                

if __name__ == '__main__':
    main()
    

"""
def update(sql):
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

"""


        