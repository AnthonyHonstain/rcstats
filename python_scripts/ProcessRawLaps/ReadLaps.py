'''
Created on Jan 4, 2012

@author: Anthony Honstain
'''
from optparse import OptionParser
import rcscoringprotxtparser
import ProcessSingleRacePGDB
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
logging.getLogger('').addHandler(console)
logger1 = logging.getLogger('UploadToPostgres')

    
        
def main():
    parser = OptionParser()

    parser.add_option("-i", "--pipe", action="store_true", dest="pipe", default=False,
                      help="Accept contents of absolute filenames as pipe.")

    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")

    parser.add_option("-d", "--database", dest="database",
                      help="database name")

    parser.add_option("-u", "--username", dest="username",
                      help="User name for database")

    parser.add_option("-p", "--password", dest="password",
                      help="Password for database")

    (options, args) = parser.parse_args()
    
    if (options.pipe):
        filenames = sys.stdin.read().split('\n')
    else:
        filenames = [options.filename,]
    
    for filename in filenames:
        if (filename == ''): continue # This happens because how I take the pipe

        #
        # Warning - SingleRace and it's parsing are not super robust, additional white
        # lines before and after may throw it off.
        #
        try:
            logger1.info("Starting processing of new file: " + filename)
            with open(filename) as f: 

                content = f.readlines()
                
                currentRaceStartIndex = 0
                lastRace = ""
                
                #Process the first race.
                for i in range(1, len(content)):
                    if (content[i].find('www.RCScoringPro.com') != -1):
                        # This means we have found a new race in the file.
                    
                        # print "=" * 100
                        # print content[currentRaceStartIndex:i]
                        
                        # This is a special check, if they have modified the race
                        # manually, there will two results for the same race and
                        # we want to take the second.
                        if (lastRace == content[currentRaceStartIndex + 4]):
                            logger1.warning("Spotting a manual intervention by director in race:{0}".format(lastRace))
                            currentRaceStartIndex = i
                            continue
                    
                        singleRace = rcscoringprotxtparser.RCScoringProTXTParser(filename, content[currentRaceStartIndex:i])
                        # Put the results in the Postgres SQL server.
                        ProcessSingleRacePGDB.ProcessSingleRacePGDB(singleRace, 
                                                                    options.database, 
                                                                    options.username, 
                                                                    options.password)

                        lastRace = content[currentRaceStartIndex + 4]
                        currentRaceStartIndex = i

            
                # This triggers when we have found the final race in the file.
                singleRace = rcscoringprotxtparser.RCScoringProTXTParser(filename, content[currentRaceStartIndex:len(content)])
                # Put the results in the Postgres SQL server.
                ProcessSingleRacePGDB.ProcessSingleRacePGDB(singleRace, 
                                                            options.database, 
                                                            options.username, 
                                                            options.password)
  
        except IOError:
            logger1.error("Invalid filename=" + filename)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger1.error("Unable to process file: {0}".format(filename))
            logger1.debug("exception:{0} \n {1}".format(str(e), trace))

if __name__ == '__main__':        
    main()
   


