'''
Created on Jan 4, 2012

@author: Anthony Honstain

-----------------------------------------------------------------------
EXAMPLE of file this is designed to process: 
-----------------------------------------------------------------------
Scoring Software by www.RCScoringPro.com                10:32:24 PM  8/13/2011

                             Bremerton R/C Raceway

Stock Buggy A Main                                            Round# 3, Race# 5

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
                  Behlen, kyle    #4      29     8:08.626     16.084           
             Honstain, Anthony    #2      28     8:00.509     16.471           
                  Fabie, Edwin    #8      27     8:04.445     16.787           
                   Craig, Mike    #1      27     8:04.702     16.387      0.257
                    Jim, Reeve    #9      27     8:15.222     17.005     10.777
                   Yates, Paul    #7      26     8:01.765     17.382           
              Haselberger, Joe    #6      26     8:10.132     16.962      8.367
               Cantrell, Jason    #5      26     8:14.373     17.139     12.608
                mcneal, pierre    #3      25     8:07.776     17.303           
                     simon,joe    #10     25     8:13.158     17.903      5.382

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 3/3.804 1/2.936 7/6.013 2/3.487 4/4.118 6/5.817 10/7.72 5/4.512 8/6.310 9/6.941
 3/18.33 2/18.41 9/22.01 1/16.65 8/22.87 5/18.40 10/20.3 4/18.88 7/20.57 6/19.24
 2/17.93 3/19.76 10/23.9 1/16.25 8/22.56 6/21.97 9/22.79 4/18.41 7/22.40 5/18.80
 2/17.56 3/16.88 10/19.4 1/17.50 6/18.03 9/23.34 8/17.87 4/19.72 7/18.46 5/20.67
 3/22.22 2/17.19 10/20.0 1/16.78 8/22.16 9/21.21 7/20.11 4/18.81 6/20.60 5/18.93
 3/18.81 2/19.30 10/20.9 1/17.44 8/17.13 9/20.36 7/17.62 4/19.87 6/17.29 5/20.34
 
 3/17.20 2/20.37 10/18.1 1/20.19 8/21.23 7/18.02 6/17.81 4/16.86 5/17.81 9/19.34
 3/19.34 2/17.19 9/17.53 1/16.92 8/17.50 7/20.18 6/18.11 4/17.51 5/19.83 10/20.8
 3/17.14 2/17.08 9/18.83 1/18.36 8/20.81 7/18.55 6/17.77 4/17.04 5/18.14 10/23.8
 3/17.69 2/16.66 9/22.09 1/17.32 8/17.82 7/17.86 6/20.44 4/16.78 5/17.74 10/19.7
 3/19.72 2/16.92         1/17.16 8/18.63 7/18.13 6/17.84 4/17.55 5/21.44        
 4/20.23 2/17.75         1/16.79                         3/19.34 5/18.52        
         2/16.99         1/17.82                                                
                         1/18.00                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     27/     28/     25/     29/     26/     26/     26/     27/     27/     25/
  8:04.7  8:00.5  8:07.7  8:08.6  8:14.3  8:10.1  8:01.7  8:04.4  8:15.2  8:13.1
'''
from singlerace import SingleRace
import re

class RCScoringProTXTParser(SingleRace):
    """
    SingleRace is will parse the www.RCScoringPro.com printout sheet
    and extract the following properties:
        filename - The file name that this race came from.
                   
        date - The date of the race.
        trackName - The header for the race (commonly the race track).
        raceClass - The class ('Stock Buggy A-Main' etc).
        roundNumber - Not all results have a round number
        raceNumber - Not all results have a race number
        
        Note - The following are spec'd in more detail below
        raceHeaderData = [] # List of Dictionaries
        lapRowsTime = [] # List of Lists
        lapRowsPosition = []
        
        
    Parsing takes the following steps.
        Starting with a list of all the LINES in the race results.
        
    [Stage 1]  Separate the lines into their distinct groups
            _raceHeaderData_RAW            
            _columnHeaders            
            _lapRowsRaw            
    
    [Stage 2] Process the raw laps data.
        lapRowsTime
            [ ['', '', '', ... ] # For Racer #1
              ['20.19', 18.63', ...] # For Racer #2
            ]
        lapRowsPosition
    
    [Stage 3] Process the header data
        raceHeaderData
            {"Driver":"John Doe", 
             "Car#":9, 
             "Laps":26, 
             "RaceTime":"8:07.943", 
             "Fast Lap":"17.063", 
             "Behind":"6.008",
             "Final Position":10}
    """
            

    def __init__(self, filename, singleRaceLines):
        '''
        Constructor - Will initialize all the required properties.
        '''
        super(RCScoringProTXTParser, self).__init__()
        
        # The raw data rows from the text file.
        #     HAVE NOT BEEN PARSED YET
        self._raceHeaderData_RAW = []
        self._columnHeaders = ""
        self._lapRowsRaw = []
        self._singleRaceLines = singleRaceLines
        
        self.filename = filename
        
        # ===================================================
        # Stage 1
        # ===================================================
        self._initial_Processing_Raw_Lines()
        

        # ===================================================
        # Stage 2 - Process the _lapRowsRaw data
        # ===================================================
        self._process_Raw_Lap_Rows()
        
        
        # ====================================================
        # Stage 3 - Process the _raceHeaderData_RAW
        # ====================================================
        self._process_Raw_Header_Rows()


    def _initial_Processing_Raw_Lines(self):
        """
        Process the file lines into initial raw structures. 
        Responsible for setting the following properties
            _raceHeaderData_RAW
            _columnHeaders
            _lapRowsRaw
            
        STAGE 1
        """
        
        '''
        # IMPORTANT EXPLANATION FOR RACES WITH PACE DATA.    
        # Some race results have the pace for the lap included in the results
         ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
         6/37.57 5/32.86 4/31.55         3/29.97 2/29.45 1/29.18                        
         10/15.7 11/01.4 12/18.7         13/29.7 13/22.8 13/19.3                        

         6/20.12 5/22.57 4/20.81         1/19.34 3/22.50 2/22.56                        
         13/15.1 13/00.3 14/06.5         15/09.8 14/03.7 14/02.1                        

         6/19.56 5/20.44 4/21.30         1/20.43 3/20.52 2/19.76                        
         14/00.6 15/19.3 15/08.3         16/12.0 15/02.3 16/21.3                        

         6/24.54 4/21.61 3/19.91         1/19.21 2/19.79 5/28.67
         
         # We want to check if laps 3,6,9 are all empty
        EXAMPLE - print singleRaceLines
         '/37.57 5/32.86 4/31.55         3/29.97 2/29.45 1/29.18', 
         ' 10/15.7 11/01.4 12/18.7         13/29.7 13/22.8 13/19.3', 
         '',
        '''
        
        pacedata_included = None # If there is pace data, this will be used as a counter. 
                
        lapData = False
        for index in range(len(self._singleRaceLines)):
                                        
            line = self._singleRaceLines[index]
            
            # Look for the column data
            if not lapData and (line.find('__10') != -1):
                # ___1___ ___2___ ___3___ ___4___ ___5___ 
                if not line.find('__1__'):
                    raise Exception("The column header data spilled into a new line")
                self._columnHeaders = line.strip('\r\n')
                lapData = True
                                
                # Check to see if pace data is mixed in - this is a strong indicator.
                index = self._singleRaceLines.index(line)
                #print "DEBUG TEST:"
                #for line in self._singleRaceLines[index:]:
                #    print line 
                               
                if (self._singleRaceLines[index + 3].strip() == '' and 
                    self._singleRaceLines[index + 6].strip() == '' and 
                    self._singleRaceLines[index + 9].strip() == ''): 
                    #raise Exception("This file format not supported, cannot mix pace data in with lap times.")
                    pacedata_included = 0
                
            # Get the laps in row format
            elif lapData:
                # If we are the end of the lap data
                if (line.find('-----') != -1):                    
                    # Example: ' ------- ------- ------- ------- '
                    index += 2 # WARNING - This is for additional laps logic below. 
                    break
 
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                # Special code for dealing with pace data.
                if (pacedata_included == None): # Common case (no pace data)
                    # Warning - we dont want to blanket strip this (white space matters)
                    self._lapRowsRaw.append(line.strip('\r\n'))
                else: # Special case (pace data mixed in).
                    if (pacedata_included % 3 == 0):
                        self._lapRowsRaw.append(line.strip('\r\n'))
                    pacedata_included += 1
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
            # Get race header data.
            if not lapData:
                # 3/17.20 2/20.37 10/18.1 1/20.19 
                self._raceHeaderData_RAW.append(line)
        
        
        # ===================================================
        # Check to see if there additional racer data - (MORE THAN 10 RACERS)
        # ===================================================
        
        # Starting at the index, lets look for another column row.
        found_additional_laps = False
        additional_lap_index = 0
        
        for trail_index in range(index, len(self._singleRaceLines)):
            line = self._singleRaceLines[trail_index].strip('\r\n')
            
            if ((not found_additional_laps) and (line.find('__11__') != -1)):                
                found_additional_laps = True
                self._columnHeaders += line
                if (pacedata_included != None):
                    pacedata_included = 0
                
            elif found_additional_laps:
                if (line.find('-----') != -1):                   
                    # Indicates there is no more data
                    #     Example: ' ------- ------- ------- ------- ' 
                    break
                
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                # Special code for dealing with pace data.
                if (pacedata_included == None): # Common case (no pace data)
                    self._lapRowsRaw[additional_lap_index] += line
                    additional_lap_index += 1
                else: # Special case (pace data mixed in)
                    if (pacedata_included % 3 == 0):
                        self._lapRowsRaw[additional_lap_index] += line
                        additional_lap_index += 1
                    pacedata_included += 1
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
                
            
    def _process_Raw_Lap_Rows(self):
        """
        Parse the _lawRowsRaw data to produce the lapRowsTime and lapRowsPosition data.  

        STAGE 2
        
        NOTE - We are going to keep empty laps, it is useful information 
            for the end user.
        """
        
        # For each racer we are going to add a list to to lapRowsTime and lapRowsPosition
        # lapRowsTime[0] will contain Racer #1's lap data (may be an empty string).
        
        # Example of self._columnHeaders.split()
        #     ['___1___', '___2___', '___3___', '___4___', '___5___', 
        #      '___6___', '___7___', '___8___', '___9___', '___10__']
        split_columns = self._columnHeaders.split()
          
        max_racers = len(split_columns)
        for index in range(len(split_columns)):
            self.lapRowsTime.append([])
            self.lapRowsPosition.append([])    
            
        '''
        For each _lapRowsRaw we are going to parse using a FIXED width, which we 
        calculate using the _columnHeaders.
        NOTE -  Split is not going to work because it trims: racerSplit = row.split() 
            (the empty spaces have meaning).
        
        Need to parse the row
            Example:
                 "3/3.804 1/2.936 7/6.013 2/3.487 4/4.118 6/5.817 10/7.72 5/4.512 8/6.310 9/6.941"
            Another Example:
                "         1/20.27 3/20.87 2/19.54                                                "
                
        Print line debugging
                Row:'         1/23.70 3/23.00 2/21.27                                                '
                raceIndex:2 lapWidth:6
                i: 17 '3/23.00'
                lapRowsTime:['27.50', '20.19', '21.93', '24.01', '20.81', 
                                '19.15', '21.15', '21.07', '21.00', '22.12', '20.87', '20.39']
                lapRowsPos:['3', '3', '2', '3', '3', '3', '3', '2', '2', '2', '3', '3']
        
                print
                print "Row:'" + row + "'"
                print "racer_index:" + str(racer_index) + " lap_width:" + str(lap_width)
                print "index:", index, "'" + row[index:index+lap_width + 1] + "'" 
                print "lapRowsTime:" + str(self.lapRowsTime[racer_index])
                print "lapRowsPos:" + str(self.lapRowsPosition[racer_index])
        '''
        # WARNING Special Code - we use the columnHeaders to identify the fixed with 
        #     that the columns are using.
        #     Explanation - Ignoring the first character [1:], find the next empty space.
        lap_width = self._columnHeaders[1:].find(' ') - 1
        
        for row in self._lapRowsRaw:                        
            index = 1
            racer_index = 0
            while index < len(row):
                if (racer_index >= max_racers):
                    raise Exception("Error in the _lapRowsRaw resulting in" +\
                                    " incorrect parsing (laps for more racers than expected")
                pos, lap = self._parse_Lap(row[index:index+lap_width + 1])
                self.lapRowsPosition[racer_index].append(pos)
                self.lapRowsTime[racer_index].append(lap)
                
                index += lap_width + 2 # +2 to skip the ' ' space.
                racer_index += 1
  

    def _process_Raw_Header_Rows(self):
        """        
        Parse the header data in _raceheaderData_RAW to extract the general
        race information, and the final stats for each racer (position,
        time, etc).
        
        STAGE 3
        
        Example of self._raceHeaderData_RAW
            ['Scoring Software by www.RCScoringPro.com                8:29:37 PM  01/14/2012', 
            '', 
            '                               TACOMA R/C RACEWAY', 
            '', 
            'MODIFIED SHORT COURSE B Main                                  Round# 3, Race# 18', 
            '', 
            '________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_', 
            'JONES, GREG\t\t\t#2 \t\t16\t\t 5:33.539\t\t 19.147\t\t          ', 
            'LEONARD, DMITRI\t\t\t#4 \t\t15\t\t 5:24.548\t\t 19.540\t\t          ', 
            'KILE, CORRY\t\t\t#3 \t\t14\t\t 5:03.416\t\t 19.153\t\t          ', 
            'MIKE CRAIG\t\t\t#1 \t\t 0\t\t    0.000\t\t       \t\t          ', 
            '']
        """
                
        #
        # Step 1 - is to get the general race information.
        #
        if len(self._raceHeaderData_RAW) < 5:
            raise Exception("The header for this race is malformed:%s" % self._raceHeaderData_RAW)
        self.date = self._parse_Header_Date(self._raceHeaderData_RAW[0])
        
        self.trackName = self._raceHeaderData_RAW[2].strip()
        
        race_class_raw, self.roundNumber, self.raceNumber = \
            self._parse_Class_And_Race_Data(self._raceHeaderData_RAW[4])
        
        # Extract the main event and main event round info from the class data.
        # Example: race classes often contain information like "Mod Buggy A-main"
        self.raceClass, self.mainEvent, self.mainEventRoundNum, self.mainEventParsed = \
            self._parse_Class_Main_Event_Info(race_class_raw)
                
        #
        # Step 2 - is to process the general race results for each racer.
        #
        individualResult = self._raceHeaderData_RAW[7:-1]
        finalRacePosition = 0;
        
        '''
        We tackle this part in several distinct peices.
        
        1. Starting with the line:
            'Fname RacerLastName\t\t\t#9 \t\t26\t\t 8:07.943\t\t 17.063\t\t     6.008\n'
            
        2. We break up the line based on the '#'
            'Fname RacerLastName' and '#9 \t\t26\t\t 8:07.943\t\t 17.063\t\t     6.008\n'
            
        3. Then we perform a split on the rest of the data 
            ['#9', '26', '8:07.943', '17.063', '6.008']
            
            We must do additional checking because the final three columns are not
            guaranteed to be there.
        '''
        for line in individualResult:
            
            finalRacePosition += 1
            driver = line[:line.find("#")].strip()
            
            # Cut off the racer names to simplify things.
            racedata = line[line.find("#"):]
            lineList = racedata.split()
                                
            
            carRaw = lineList[0]
            if (carRaw[0] != '#'):
                raise Exception("Incorrect format for header data, execting a '#' in the car number, line: " + line)
            car = int(carRaw[1:])
            
            laps = int(lineList[1])
            
            # WARNING - The following fields may not be present.
            racetime = lineList[2]
            if (line.find(':') <= 0): # Checking to see if the racer even has a race time.
                racetime = ''
            
            fastlap = ''
            behind = ''
            if (len(lineList) >= 4):
                fastlap = lineList[3]
            if len(lineList) == 5:
                behind = lineList[4]
            
            self.raceHeaderData.append({"Driver":driver, 
                                        "Car#":car, 
                                        "Laps":laps, 
                                        "RaceTime":racetime, 
                                        "Fast Lap":fastlap, 
                                        "Behind":behind,
                                        "Final Position":finalRacePosition})
            
   
    def _parse_Header_Date(self, rawDateLine):
        #Scoring Software by www.RCScoringPro.com                10:32:24 PM  8/13/2011
        trimmedDate = rawDateLine[41:].strip()
        return trimmedDate
            
            
    def _parse_Class_And_Race_Data(self, rawClassData):
        #Stock Buggy A Main                                            Round# 3, Race# 5        
        roundIndex = rawClassData.find("Round#")    
        raceClass = rawClassData[:roundIndex].strip()
        round_num = rawClassData[roundIndex:].split(',')[0].split()[1]
        race_num = rawClassData[roundIndex:].split(',')[1].split()[1]
        return (raceClass, round_num, race_num)
    
    
    def _parse_Class_Main_Event_Info(self, race_class_raw):
        '''        
        Examples of what we want to process:
            "Mod Buggy A-main"
            "Mod Buggy A main"
            "Pro 4 A3 main"
            "Pro 4 B2 main"
        '''
        pattern = re.compile("[A-Z][1-9]?.main", re.IGNORECASE)
    
        match = pattern.search(race_class_raw)
        if not match:
            # Nothing to do if we don't spot a main event.            
            #print 'Ignoring:', race_class_raw            
            return race_class_raw, None, None, None
        
        start_index = match.start(0)
    
        # Fields we want to parse out
        cleaned_raceclass_name = ""
        main_event = None # Indicates A,B,C, etc main event
        main_event_round_num = None # Indicates the round for multiple main events A1, C2, etc.
                
        race_class_raw = race_class_raw.replace('-', ' ')
                
        # We want to trim off the 'A main' part of the string and clean it up.
        cleaned_raceclass_name = race_class_raw[:start_index]
        # I added an additional cleanup, since I saw some older results with extra
        # junk characters in the name.
        
        # Example - "Mod Buggy"
        cleaned_raceclass_name = cleaned_raceclass_name.strip('+- ')
        
        # Example - "A Main"
        main_event_raw = race_class_raw[start_index:].strip('+- ')    

        # The regex means there must be a white space here.        
        main_event_round_raw = main_event_raw.split()[0]
        
        # Convert the character 'A','B', into the corresponding int for the db.
        # "A" -> 65
        main_event = ord(main_event_round_raw[0].upper()) - 64 
        
        if len(main_event_round_raw) > 1:
            # We are looking for the case like: "A1", "A3"
            # I have left it open to the possibility of multiple B,C, etc.
            main_event_round_num = int(main_event_round_raw[1:])
                
        #print 'raceclass:{0:25} mainevent:{1} maineventroundnumber:{2:5} Orig:{3} '.format(cleaned_raceclass_name, main_event, main_event_round_num, race_class_raw)

        return cleaned_raceclass_name, main_event, main_event_round_num, main_event_raw
    
            
    def _parse_Lap(self, rawLap):
        # rawLap will have the form of 3/3.804
        if rawLap.find('/') == -1:
            return ("", "")
        
        splitLap = rawLap.split('/')
        return (splitLap[0], splitLap[1])

