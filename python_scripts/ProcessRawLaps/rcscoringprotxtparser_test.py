'''
Created on May 13, 2012

@author: Anthony Honstain
'''

import unittest
from rcscoringprotxtparser import RCScoringProTXTParser
    
    
singleRaceSimple = '''Scoring Software by www.RCScoringPro.com                8:09:03 PM  01/14/2012

                               TACOMA R/C RACEWAY

MODIFIED BUGGY B-Main                                         Round# 3, Race# 16

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Matesa, Ryan            #2         28         8:10.270         16.939                  
DIBRINO, ANDY            #3         28         8:13.744         16.748             3.474
JOWERS, ROBERT            #4         27         8:01.288         16.874                  
HONSTAIN, ANTHONY            #8         27         8:11.316         17.290            10.028
GOULD, CHRIS            #1         27         8:11.756         16.900            10.468
CHERRY, GEORGE            #5         27         8:17.078         17.426            15.790
TRAVIS SCHREVEN            #7         26         8:01.935         16.613                  
RASHEED, DEREK            #6         26         8:02.970         17.008             1.035
ROGER SEIM            #10        26         8:04.489         17.121             2.554
TOM WAGGONER            #9         26         8:07.943         17.063             6.008

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 10/24.5 1/20.58 3/22.32 6/23.85 4/23.14 5/23.45 2/21.97 8/24.19 9/24.35 7/23.92
 8/18.04 1/17.09 5/19.28 9/19.79 3/17.67 4/17.72 2/17.83 7/18.19 10/20.0 6/18.13
 8/17.53 1/16.93 4/17.02 9/17.43 3/17.66 5/17.98 2/17.22 7/17.34 10/19.4 6/17.26
 5/17.34 1/17.11 3/17.65 7/17.67 9/22.07 8/20.90 2/18.20 4/17.56 10/20.8 6/19.10
 4/17.13 1/17.25 3/17.96 6/17.16 9/17.42 8/17.60 2/18.27 5/17.74 10/17.3 7/18.50
 4/17.30 1/17.25 3/17.26 6/17.65 9/19.12 8/18.86 2/17.14 5/17.76 10/17.5 7/17.19
 4/17.21 1/16.99 3/17.17 6/17.42 9/17.63 8/17.75 2/17.92 5/17.59 10/17.5 7/19.47
 2/17.42 1/17.44 5/20.61 3/17.32 9/17.48 8/17.46 4/20.34 6/19.75 10/17.3 7/17.26
 2/17.14 1/17.33 4/17.39 3/17.60 9/18.96 8/19.20 7/21.09 5/17.41 10/18.5 6/17.34
 2/17.18 1/17.56 4/16.74 3/17.38 9/21.50 10/22.4 6/18.16 5/19.21 8/18.10 7/22.36
 2/17.47 1/17.31 4/17.49 3/16.88 9/18.12 10/17.8 7/20.85 5/17.53 8/18.10 6/17.75
 2/17.01 1/17.35 4/16.87 3/17.26 9/19.50 8/18.13 10/23.2 5/17.72 6/18.36 7/19.70
 2/17.21 1/18.07 4/17.10 3/16.97 8/17.55 10/23.3 9/17.77 5/18.00 6/17.10 7/18.20
 2/19.16 1/17.31 3/17.16 4/18.11 6/17.63 10/17.9 9/18.11 5/17.59 7/21.18 8/21.60
 2/17.03 1/18.23 3/17.14 4/17.30 6/17.76 10/19.0 9/20.36 5/17.54 7/17.56 8/17.80
 4/19.43 1/17.40 2/18.27 3/18.04 6/17.53 10/18.9 9/17.70 5/17.77 8/20.34 7/17.22
 4/17.24 1/17.32 2/16.86 3/17.12 6/18.08 10/17.1 9/17.03 5/19.33 8/17.13 7/17.19
 4/17.43 1/17.15 2/17.15 3/17.52 6/17.88 10/17.0 9/17.36 5/17.65 8/17.06 7/17.65
 4/17.31 1/17.31 2/17.41 3/17.12 6/17.57 10/17.6 9/17.01 5/17.29 8/17.56 7/17.12
 4/16.90 1/17.47 2/17.02 3/16.87 6/17.80 10/17.2 8/17.54 5/18.06 9/20.40 7/17.58
 4/17.33 1/17.31 2/17.14 3/17.08 6/17.52 10/17.0 8/17.27 5/18.06 9/17.62 7/18.30
 4/17.17 1/17.42 2/17.15 3/17.82 6/18.35 9/18.27 8/18.52 5/18.12 10/24.2 7/17.48
 4/24.36 1/18.37 2/17.37 3/20.07 6/17.81 9/17.20 8/16.61 5/17.55 10/17.4 7/17.91
 5/21.31 1/17.47 2/17.36 3/17.00 6/17.60 9/17.25 8/17.07 4/17.61 10/17.9 7/17.49
 5/17.24 1/17.34 2/17.20 3/17.26 6/17.88 8/17.78 7/17.89 4/17.69 10/17.2 9/23.20
 4/17.02 1/17.36 2/17.32 3/17.40 6/17.65 8/17.54 7/19.32 5/17.86 10/17.3 9/17.66
 5/20.17 1/17.27 2/16.93 3/18.05 6/18.07                 4/19.08                
         1/17.14 2/17.27                                                        
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     27/     28/     28/     27/     27/     26/     26/     27/     26/     26/
  8:11.7  8:10.2  8:13.7  8:01.2  8:17.0  8:02.9  8:01.9  8:11.3  8:07.9  8:04.4
'''

class TestSingleRaceSimple(unittest.TestCase):

    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("test_filename", singleRaceSimple.split('\n'))

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader). 
        expectedLaps = ["24.5", "18.04", "17.53", "17.34", "17.13", "17.30", "17.21", "17.42", "17.14", "17.18", "17.47", "17.01", "17.21", "19.16", "17.03", "19.43", "17.24", "17.43", "17.31", "16.90", "17.33", "17.17", "24.36", "21.31", "17.24", "17.02", "20.17", ""]
        
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])

    def test_racerTwo(self):
        expectedLaps = ["20.58", "17.09", "16.93", "17.11", "17.25", "17.25", "16.99", "17.44", "17.33", "17.56", "17.31", "17.35", "18.07", "17.31", "18.23", "17.40", "17.32", "17.15", "17.31", "17.47", "17.31", "17.42", "18.37", "17.47", "17.34", "17.36", "17.27", "17.14"]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[1])
#
    def test_racerTen(self):
        expectedLaps = ["23.92", "18.13", "17.26", "19.10", "18.50", "17.19", "19.47", "17.26", "17.34", "22.36", "17.75", "19.70", "18.20", "21.60", "17.80", "17.22", "17.19", "17.65", "17.12", "17.58", "18.30", "17.48", "17.91", "17.49", "23.20", "17.66", "", ""]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[9])
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.singe_test_race.date)
        self.assertEqual("MODIFIED BUGGY", self.singe_test_race.raceClass)
        self.assertEqual(2, self.singe_test_race.mainEvent)
        self.assertEqual(None, self.singe_test_race.mainEventRoundNum)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("16", self.singe_test_race.raceNumber)
        
        self.assertEqual(self.singe_test_race.raceHeaderData[-1], 
                         {"Driver":"TOM WAGGONER", 
                          "Car#":9, 
                          "Laps":26, 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":10})



class TestSingleRaceSimpleTextFile(unittest.TestCase):

    def setUp(self):   
        self.filename = "TestFile_SingleRaceSimple.txt"
        with open(self.filename) as f: 
            content = f.readlines()     
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_filename(self):
        self.assertEqual(self.filename, self.singe_test_race.filename)

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader). 
        expectedLaps = ["24.5", "18.04", "17.53", "17.34", "17.13", "17.30", "17.21", "17.42", "17.14", "17.18", "17.47", "17.01", "17.21", "19.16", "17.03", "19.43", "17.24", "17.43", "17.31", "16.90", "17.33", "17.17", "24.36", "21.31", "17.24", "17.02", "20.17", ""]
        
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])

    def test_racerTwo(self):
        expectedLaps = ["20.58", "17.09", "16.93", "17.11", "17.25", "17.25", "16.99", "17.44", "17.33", "17.56", "17.31", "17.35", "18.07", "17.31", "18.23", "17.40", "17.32", "17.15", "17.31", "17.47", "17.31", "17.42", "18.37", "17.47", "17.34", "17.36", "17.27", "17.14"]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[1])

    def test_racerTen(self):
        expectedLaps = ["23.92", "18.13", "17.26", "19.10", "18.50", "17.19", "19.47", "17.26", "17.34", "22.36", "17.75", "19.70", "18.20", "21.60", "17.80", "17.22", "17.19", "17.65", "17.12", "17.58", "18.30", "17.48", "17.91", "17.49", "23.20", "17.66", "", ""]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[9])
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.singe_test_race.date)
        self.assertEqual("MODIFIED BUGGY", self.singe_test_race.raceClass)
        self.assertEqual(2, self.singe_test_race.mainEvent)
        self.assertEqual(None, self.singe_test_race.mainEventRoundNum)
        self.assertEqual("B Main", self.singe_test_race.mainEventParsed)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("16", self.singe_test_race.raceNumber)
        
        self.assertEqual(self.singe_test_race.raceHeaderData[-1], 
                         {"Driver":"TOM WAGGONER", 
                          "Car#":9, 
                          "Laps":26, 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":10})


class TestMoreThanTenTextFile(unittest.TestCase):

    def setUp(self):   
        self.filename = "TestFile_12manrace.txt"
        with open(self.filename) as f: 
            content = f.readlines()     
        self.singe_test_race = RCScoringProTXTParser(self.filename, content)

    def test_filename(self):
        self.assertEqual(self.filename, self.singe_test_race.filename)
      
    def test_columns(self):
        expected_column_line = " ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__ ___11__ ___12__ ___13__ ___14__ ___15__ ___16__ ___17__ ___18__ ___19__ ___20__"
        self.assertEqual(expected_column_line, self.singe_test_race._columnHeaders)
        
    def test_racerTwelve(self):
        expectedLaps = ["26.71",    "17.82",    "17.47",    "17.55",    "16.88",    "18.07",    "18.56",    "17.64",    "17.28",    "22.71",    "23.33",    "20.20",    "17.49",    "17.80",    "17.27",    "17.59",    "17.98",    "17.97",    "20.91",    "18.00",    "19.47",    "20.52",    "19.17",    "17.08",    "17.42",    "20.00",    "",    "",    "",]

        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[11])
    

singleRaceModified ='''Scoring Software by www.RCScoringPro.com                10:36:55 PM  01/14/2012

                               TACOMA R/C RACEWAY

4WD MODIFIED A2 Main                                          Round# 3, Race# 30

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
SCHOETLER, MICHAEL            #1         22         6:04.123         15.794                  
SMITH, LUKE            #2         22         6:06.384         15.759             2.261
Barnes, Marty            #3         22         6:06.896         16.095             2.773
BRIAN MUNN            #6         22         6:30.514         16.241            26.391
WALENTIA, JOHN            #5         21         6:07.583         15.908                  
AUSTIN SEIM            #7         21         6:10.454         16.248             2.871
HONSTAIN, ANTHONY            #8         21         6:13.906         16.425             6.323
DIBRINO, ANDY            #4         16         4:27.016         16.087                  
MATESA, TANNER            #9          4         1:20.392         17.097                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 9/35.00 8/34.64 1/19.87 2/20.26 6/25.95 5/25.66 3/24.05 7/26.66 4/25.46        
 8/15.85 9/16.58 1/16.67 2/17.01 5/17.55 4/17.29 3/17.22 6/17.41 7/20.34        
                 1/16.25 2/16.73 5/16.25 4/16.43 3/17.05 6/16.59 7/17.48        
 1/15.79 2/16.27 3/16.48 4/16.16 7/17.28 6/17.24 5/16.83 8/17.42 9/17.09        
 1/15.90 2/15.89 3/16.36 4/16.08 7/16.21 6/16.44 5/17.09 8/17.11                
 1/16.06 2/15.75 3/16.33 4/16.59 8/19.65 5/16.44 6/17.78 7/17.10                
 1/15.85 2/16.34 3/16.59 4/16.68 8/19.06 5/16.69 6/16.93 7/16.42                
 1/15.86 2/16.13 3/16.20 4/16.48 8/16.08 5/16.53 6/16.73 7/16.49                
 1/16.16 2/15.87 3/16.11 4/16.19 8/16.84 5/16.51 6/16.95 7/16.89                
 1/17.00 2/16.49 3/16.22 4/16.08 8/16.10 5/16.35 6/16.78 7/16.76                
 1/15.82 2/18.69 3/16.41 4/16.32 8/16.17 5/16.55 6/16.61 7/17.81                
 1/16.32 2/16.08 3/16.10 4/16.75 8/16.84 5/17.12 6/16.85 7/17.20                
 1/16.23 2/15.96 3/16.32 4/16.31 7/18.92 5/16.62 6/16.49 8/19.52                
 1/17.29 2/17.14 3/16.57 4/16.60 7/16.66 5/16.24 6/19.76 8/17.98                
 1/18.50 2/16.23 3/16.62 4/16.60 7/16.13 5/16.74 6/17.72 8/16.99                
 1/16.30 2/16.34 3/16.17 4/16.11 7/16.99 5/16.92 6/16.84 8/17.78                
 1/16.60 2/16.65 3/16.97         6/18.70 4/16.89 5/18.24 7/16.73                
 2/18.49 3/19.97 1/16.51         5/16.46 4/16.77 6/18.71 7/16.70                
 2/16.06 3/15.95 1/16.09         5/16.38 4/17.32 6/16.24 7/17.04                
 1/16.56 3/16.33 2/17.91         5/15.90 4/16.34 6/18.22 7/16.96                
 1/15.98 3/16.29 2/16.61         5/17.36 4/16.82 6/17.26 7/20.27                
 1/16.39 2/16.69 3/17.43                 4/30.51                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     22/     22/     22/     16/     21/     22/     21/     21/      4/        
  6:04.1  6:06.3  6:06.8  4:27.0  6:07.5  6:30.5  6:10.4  6:13.9  1:20.3        
'''
        
class TestSingleRaceModified(unittest.TestCase):

    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("testfilename", singleRaceModified.split('\n'))

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader). 
        expectedLaps = ["35.00", "15.85", "", "15.79", "15.90", "16.06", "15.85", "15.86", "16.16", "17.00", "15.82", "16.32", "16.23", "17.29", "18.50", "16.30", "16.60", "18.49", "16.06", "16.56", "15.98", "16.39"]
                        
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])

    def test_racerFour(self):
        expectedLaps = ["20.26", "17.01", "16.73", "16.16", "16.08", "16.59", "16.68", "16.48", "16.19", "16.08", "16.32", "16.75", "16.31", "16.60", "16.60", "16.11", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[3])

    def test_racerTen(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(len(expectedLaps), len(self.singe_test_race.lapRowsTime[9]))
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[9])
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.singe_test_race.date)
        self.assertEqual("4WD MODIFIED", self.singe_test_race.raceClass)
        self.assertEqual(1, self.singe_test_race.mainEvent)
        self.assertEqual(2, self.singe_test_race.mainEventRoundNum)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("30", self.singe_test_race.raceNumber)
        
        self.assertEqual(self.singe_test_race.raceHeaderData[-1], 
                         {"Driver":"MATESA, TANNER", 
                          "Car#":9, 
                          "Laps":4, 
                          "RaceTime":"1:20.392", 
                          "Fast Lap":"17.097", 
                          "Behind":"",
                          "Final Position":9})
        

     
singleRaceEarlyDrop = '''Scoring Software by www.RCScoringPro.com                8:29:37 PM  01/14/2012

                               TACOMA R/C RACEWAY

MODIFIED SHORT COURSE B Main                                  Round# 3, Race# 18

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
JONES, GREG			#2 		16		 5:33.539		 19.147		          
LEONARD, DMITRI			#4 		15		 5:24.548		 19.540		          
KILE, CORRY			#3 		14		 5:03.416		 19.153		          
MIKE CRAIG			#1 		 0		    0.000		       		          

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
         1/24.85 3/27.50 2/26.13                                                
         1/20.00 3/20.19 2/21.22                                                
         1/20.41 2/21.93 3/22.72                                                
         1/19.97 3/24.01 2/21.98                                                
         1/20.28 3/20.81 2/20.87                                                
         1/20.27 3/19.15 2/20.24                                                
         1/20.29 3/21.15 2/19.61                                                
         1/20.27 2/21.07 3/25.53                                                
         1/20.00 2/21.00 3/20.11                                                
         1/19.14 2/22.12 3/20.78                                                
         1/20.27 3/20.87 2/19.54                                                
         1/19.92 3/20.39 2/21.28                                                
         1/23.70 3/23.00 2/21.27                                                
         1/20.33 3/20.16 2/20.78                                                
         1/21.26         2/22.43                                                
         1/22.50                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      0/     16/     14/     15/                                                
     0.0  5:33.5  5:03.4  5:24.5                                                

'''

class TestSingleRaceRacerDropped(unittest.TestCase):
 
    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("t1", singleRaceEarlyDrop.split('\n'))

    def test_racerOne(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[0])
        
        self.assertEqual(2, self.singe_test_race.mainEvent)

    def test_racerTwo(self):
        expectedLaps = ["24.85", "20.00", "20.41", "19.97", "20.28", "20.27", "20.29", "20.27", "20.00", "19.14", "20.27", "19.92", "23.70", "20.33", "21.26", "22.50"]
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[1])
        
    def test_initial_processing(self):
        
        expected_column_line = " ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__"
        self.assertEqual(expected_column_line, self.singe_test_race._columnHeaders)
        
        expected_lap_lines = ['         1/24.85 3/27.50 2/26.13                                                ', 
                              '         1/20.00 3/20.19 2/21.22                                                ', 
                              '         1/20.41 2/21.93 3/22.72                                                ', 
                              '         1/19.97 3/24.01 2/21.98                                                ', 
                              '         1/20.28 3/20.81 2/20.87                                                ', 
                              '         1/20.27 3/19.15 2/20.24                                                ', 
                              '         1/20.29 3/21.15 2/19.61                                                ', 
                              '         1/20.27 2/21.07 3/25.53                                                ', 
                              '         1/20.00 2/21.00 3/20.11                                                ', 
                              '         1/19.14 2/22.12 3/20.78                                                ', 
                              '         1/20.27 3/20.87 2/19.54                                                ', 
                              '         1/19.92 3/20.39 2/21.28                                                ', 
                              '         1/23.70 3/23.00 2/21.27                                                ', 
                              '         1/20.33 3/20.16 2/20.78                                                ', 
                              '         1/21.26         2/22.43                                                ', 
                              '         1/22.50                                                                ']
        self.assertEqual(expected_lap_lines, self.singe_test_race._lapRowsRaw)
        
        expected_header_data = ['Scoring Software by www.RCScoringPro.com                8:29:37 PM  01/14/2012', 
                                '', '                               TACOMA R/C RACEWAY', 
                                '', 
                                'MODIFIED SHORT COURSE B Main                                  Round# 3, Race# 18', 
                                '', 
                                '________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_', 
                                'JONES, GREG\t\t\t#2 \t\t16\t\t 5:33.539\t\t 19.147\t\t          ', 
                                'LEONARD, DMITRI\t\t\t#4 \t\t15\t\t 5:24.548\t\t 19.540\t\t          ', 
                                'KILE, CORRY\t\t\t#3 \t\t14\t\t 5:03.416\t\t 19.153\t\t          ', 
                                'MIKE CRAIG\t\t\t#1 \t\t 0\t\t    0.000\t\t       \t\t          ', 
                                '']
        self.assertEqual(expected_header_data, self.singe_test_race._raceHeaderData_RAW)



singleRaceWithBrokeRacer = '''Scoring Software by www.RCScoringPro.com                9:10:24 PM  01/14/2012

                               TACOMA R/C RACEWAY

4WD MODIFIED A1 Main                                          Round# 3, Race# 22

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
SCHOETLER, MICHAEL            #1         23         6:15.854         15.552                  
SMITH, LUKE            #2         22         6:02.864         15.808                  
Barnes, Marty            #3         22         6:07.925         15.906             5.061
WALENTIA, JOHN            #5         22         6:11.373         16.058             8.509
DIBRINO, ANDY            #4         21         6:00.911         15.940                  
BRIAN MUNN            #6         21         6:05.274         16.200             4.363
HONSTAIN, ANTHONY            #8         20         6:03.032         16.662                  
MATESA, TANNER            #9         20         6:12.549         16.794             9.517
AUSTIN SEIM            #7         19         6:00.231         16.821                  
Gilley, Tres            #10         1           21.675                                 

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
         1/19.29 2/19.75 3/20.48 5/24.82 6/26.83 8/27.84 9/28.00 7/27.23 4/21.67
 1/34.59 2/16.38 3/16.58 4/16.56 5/17.24 6/17.17 9/22.09 8/19.50 7/18.80        
 3/20.47 1/16.36 2/17.13 4/18.92 5/16.96 6/16.54 9/17.50 7/17.30 8/21.02        
 3/16.10 1/15.95 2/16.21 4/16.16 5/16.60 6/16.92 9/20.37 7/16.83 8/18.06        
 3/16.23 1/16.11 2/16.46 4/16.51 5/16.29 6/16.83 9/18.54 7/16.66 8/18.99        
 3/15.55 1/15.80 2/15.90 4/16.75 5/16.69 6/17.77 9/18.69 7/16.92 8/17.18        
 3/15.82 1/16.19 2/16.32 4/16.21 5/16.54 6/17.10 9/18.83 7/17.66 8/19.18        
 2/16.22 1/15.99 3/17.15 5/21.69 4/16.45 6/17.29 9/17.39 7/17.37 8/18.34        
 2/15.68 1/16.01 3/16.24 5/16.06 4/16.39 6/16.68 9/17.73 7/18.47 8/18.11        
 2/15.73 1/17.36 3/16.38 5/16.22 4/16.33 6/16.63 9/20.26 7/19.29 8/17.18        
 2/15.90 1/15.86 3/16.59 5/16.32 4/16.32 6/16.37 9/17.91 7/17.53 8/17.43        
 2/16.05 1/16.57 3/16.32 5/15.94 4/16.23 6/16.33 9/17.59 7/16.74 8/19.66        
 2/16.03 1/16.04 3/16.51 5/19.00 4/16.39 6/16.20 9/17.98 7/16.73 8/17.58        
 2/15.99 1/15.80 3/16.10 5/16.51 4/16.24 6/17.00 9/17.98 7/16.81 8/18.84        
 2/15.95 1/16.21 3/16.42 5/17.65 4/16.86 6/17.63 9/17.79 7/17.33 8/17.05        
 2/15.79 1/15.99 3/16.68 5/17.70 4/16.06 6/17.61 9/18.40 7/17.71 8/17.88        
 1/17.01 2/18.32 3/16.56 5/17.23 4/16.37 6/16.66 9/17.62 7/17.14 8/16.79        
 1/15.79 2/16.78 3/16.09 5/16.29 4/16.51 6/17.15 9/18.83 7/16.99 8/17.77        
 1/16.05 2/16.18 3/17.97 5/16.28 4/17.32 6/16.63 9/16.82 7/16.92 8/17.27        
 1/16.03 2/17.22 3/17.44 5/16.14 4/16.21 6/17.16         7/21.04 8/18.10        
 1/15.80 2/16.20 3/16.05 5/16.22 4/16.38 6/16.69                                
 1/15.73 2/16.16 3/16.97         4/16.05                                        
 1/17.27                                                                        
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     23/     22/     22/     21/     22/     21/     19/     20/     20/      1/
  6:15.8  6:02.8  6:07.9  6:00.9  6:11.3  6:05.2  6:00.2  6:03.0  6:12.5    21.6
'''

class TestSingleRaceBrokeRacer(unittest.TestCase):

    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("testfilename", singleRaceWithBrokeRacer.split('\n'))
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.singe_test_race.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.singe_test_race.date)
        self.assertEqual("4WD MODIFIED", self.singe_test_race.raceClass)
        self.assertEqual(1, self.singe_test_race.mainEvent)
        self.assertEqual("3", self.singe_test_race.roundNumber)
        self.assertEqual("22", self.singe_test_race.raceNumber)
        
        # Gilley, Tres            #10         1           21.675                      
        self.assertEqual(self.singe_test_race.raceHeaderData[9], 
                         {"Driver":"Gilley, Tres", 
                          "Car#":10, 
                          "Laps":1, 
                          "RaceTime":"", 
                          "Fast Lap":"", 
                          "Behind":"",
                          "Final Position":10})
        # SCHOETLER, MICHAEL            #1         23         6:15.854         15.552      
        self.assertEqual(self.singe_test_race.raceHeaderData[0], 
                         {"Driver":"SCHOETLER, MICHAEL", 
                          "Car#":1, 
                          "Laps":23, 
                          "RaceTime":"6:15.854", 
                          "Fast Lap":"15.552", 
                          "Behind":"",
                          "Final Position":1})
        
        
singleRaceWithPaceData = '''Scoring Software by www.RCScoringPro.com                10:05:41 PM  03/18/2011

                               TACOMA R/C RACEWAY

STOCK BUGGY B Main                                            Round# 3, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
FRANK, JON            #5         18         6:09.135         19.183                  
JOHNSON, JJ            #6         18         6:16.021         19.456             6.886
CADDELL, ANDREW            #3         17         6:05.638         19.211                  
JOHNSON, JAMES            #7         16         5:40.504         18.829                  
MARGESON, EVAN            #1         16         6:06.879         19.568            26.375
BUTLER, BRANDON            #2         15         6:12.022         19.415                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 6/37.57 5/32.86 4/31.55         3/29.97 2/29.45 1/29.18                        
 10/15.7 11/01.4 12/18.7         13/29.7 13/22.8 13/19.3                        

 6/20.12 5/22.57 4/20.81         1/19.34 3/22.50 2/22.56                        
 13/15.1 13/00.3 14/06.5         15/09.8 14/03.7 14/02.1                        

 6/19.56 5/20.44 4/21.30         1/20.43 3/20.52 2/19.76                        
 14/00.6 15/19.3 15/08.3         16/12.0 15/02.3 16/21.3                        

 6/24.54 4/21.61 3/19.91         1/19.21 2/19.79 5/28.67                        
 15/21.8 15/05.6 16/14.3         17/18.1 16/09.0 15/15.7                        

 5/20.36 6/27.97 3/20.23         1/19.82 2/19.94 4/20.20                        
 15/06.5 15/16.4 16/04.2         17/09.8 17/21.5 15/01.1                        

 5/19.68 6/20.04 3/19.64         1/20.17 2/19.45 4/18.82                        
 16/18.3 15/03.7 17/18.1         17/05.4 17/13.0 16/11.2                        

 6/23.51 5/19.41 3/19.21         1/20.24 2/20.38 4/19.17                        
 16/18.0 16/16.9 17/10.7         17/02.3 17/09.2 16/02.0                        

 5/23.20 6/26.41 3/19.66         1/19.59 2/19.87 4/19.09                        
 16/17.1 16/22.6 17/06.2         18/19.8 17/05.3 17/17.1                        

 5/20.18 6/23.97 2/20.40         1/23.43 3/22.77 4/21.67                        
 16/11.1 16/22.7 17/04.0         17/03.1 17/07.7 17/16.2                        

 5/22.65 6/24.61 2/20.63         1/20.93 3/19.65 4/18.97                        
 16/10.3 16/23.8 17/02.7         17/02.4 17/04.4 17/10.8                        

 5/24.19 6/28.28 2/19.58         1/19.18 3/19.45 4/19.32                        
 16/11.8 15/05.7 17/00.0         18/20.2 17/01.3 17/06.9                        

 5/21.53 6/26.16 2/20.39         1/19.26 3/20.09 4/19.92                        
 16/09.5 15/07.9 18/20.0         18/17.4 18/20.8 17/04.6                        

 5/21.30 6/28.63 4/24.88         1/19.86 2/21.92 3/20.53                        
 16/07.3 15/12.7 17/03.8         18/15.9 17/00.7 17/03.4                        

 5/26.81 6/23.90 4/19.73         1/19.38 2/19.90 3/19.87                        
 16/11.7 15/11.6 17/01.8         18/13.9 18/20.2 17/01.6                        

 5/21.04 6/25.10 4/26.10         1/19.67 2/19.63 3/19.90                        
 16/09.4 15/12.0 17/07.3         18/12.6 18/18.4 17/00.0                        

 5/20.55         4/21.47         1/19.48 2/19.74 3/22.81                        
 16/06.8         17/07.1         18/11.2 18/17.0 17/01.7                        

                 3/20.07         1/19.59 2/21.16                                
                 17/05.6         18/10.1 18/17.2                                

                                 1/19.51 2/19.73                                
                                 18/09.1 18/16.0                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     16/     15/     17/             18/     18/     16/                        
  6:06.8  6:12.0  6:05.6          6:09.1  6:16.0  5:40.5      
'''
        
class TestSingleRaceWithPaceData(unittest.TestCase):
 
    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("testfilename", singleRaceWithPaceData.split('\n'))
        
    def test_racer4_laptimes(self):        
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""] # 18 laps
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[3])


elevenManRaceWithPaceData = '''Scoring Software by www.RCScoringPro.com                11:16:24 PM  03/18/2011

                               TACOMA R/C RACEWAY

MODIFIED SHORT COURSE A Main                                  Round# 3, Race# 8

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
CANTRELL, JONATHAN            #6         23         8:00.139         17.827                  
MARGESON, EVAN            #5         23         8:17.632         19.677            17.493
FRANK, JON            #1         22         8:12.675         19.432                  
KNOX, MIKE            #4         21         8:23.785         20.854                  
KEITH, BRIAN            #11        19         8:21.059         23.253                  
KEITH, SCOTT            #8         19         8:23.912         17.128             2.853
BUTLER, JAMIE            #9         14         6:08.575         22.896                  
Woods, Doug            #7          8         6:59.849         21.092                  
YOUNG, BRANDON            #2          0            0.000                                 
MAZANTI, KRIS            #10         0            0.000                            0.000

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 1/28.60                 3/32.12 2/30.30 6/38.31 8/254.2 5/36.97 7/40.05        
 17/06.2                 15/01.7 16/04.9 13/18.0  2/28.4 13/00.7 12/00.7        

 1/21.86                 3/22.25 2/20.71 4/17.82 8/23.01 6/23.11 7/24.64        
 20/24.6                 18/09.4 19/04.6 18/25.2  4/14.4 16/00.8 15/05.2        

 1/19.94                 3/20.85 2/20.58 4/20.69 8/28.15 6/25.54 7/24.38        
 21/12.9                 20/21.5 21/21.2 19/06.5  5/28.9 17/05.2 17/24.8        

 1/20.46                 3/21.66 2/20.24 4/20.37 8/23.90 6/22.44 7/26.88        
 22/19.8                 20/04.4 21/02.2 20/06.0  6/13.9 18/06.4 17/12.8        

 1/23.60                 4/25.87 2/22.81 3/21.37 8/21.09 6/25.56 7/25.03        
 21/00.8                 20/11.0 21/01.5 21/18.0  7/10.5 18/01.1 18/27.6        

 1/20.30                 4/23.07 2/21.00 3/18.88 8/21.30 6/25.39 7/22.89        
 22/14.2                 20/06.1 22/17.4 21/01.1  8/15.5 19/23.6 18/11.6        

 1/20.40                 4/21.28 2/20.33 3/18.79 8/22.15 6/23.86 7/23.61        
 22/07.7                 21/21.3 22/10.2 22/11.1  9/26.3 19/16.4 18/02.1        

 1/20.73                 4/23.83 3/21.44 2/20.25 8/26.00 6/24.19 7/23.87        
 22/03.8                 21/21.2 22/07.9 22/05.4 10/44.8 19/11.8 19/22.0        

 2/21.50                 4/20.93 3/20.43 1/18.25         6/26.31 7/26.37        
 22/02.6                 21/14.4 22/03.7 23/17.7         19/12.7 19/21.9        

 3/24.78                 4/21.90 2/23.12 1/18.34         6/24.91 7/27.23        
 22/08.8                 21/10.9 22/06.2 23/10.1         19/10.8 19/23.5        

 2/19.43                 4/26.70 3/21.42 1/20.48         6/26.70 7/24.62        
 22/03.3                 21/17.2 22/04.8 23/08.4         19/12.3 19/20.2        

 2/20.06                 4/26.80 3/19.67 1/20.39         6/27.80 7/25.99        
 23/21.6                 21/22.7 22/00.5 23/06.8         19/15.3 19/19.7        

 3/26.46                 4/25.83 2/20.90 1/21.86         6/22.96 7/23.50        
 22/07.6                 20/01.7 23/20.6 23/08.0         19/10.7 19/15.6        

 3/21.81                 4/22.21 2/21.35 1/26.38         6/24.80 7/29.43        
 22/07.1                 21/23.0 23/20.0 23/16.5         19/09.3 19/20.2        

 3/21.17                 4/22.84 2/23.33 1/18.67         6/27.03                
 22/05.7                 21/21.4 22/00.6 23/12.1         19/11.0                

 3/24.89                 4/23.04 2/20.99 1/20.15         5/34.99                
 22/09.5                 21/20.3 23/21.2 23/10.3         19/21.8                

 3/23.75                 4/21.27 2/23.33 1/18.68         6/37.57                
 22/11.5                 21/17.2 22/01.4 23/06.7         18/07.2                

 3/20.42                 4/21.28 2/21.00 1/18.64         6/17.12                
 22/09.1                 21/14.4 22/00.3 23/03.5         19/23.8                

 3/23.28                 4/23.28 2/20.76 1/22.39         6/26.56                
 22/10.3                 21/14.1 23/20.9 23/05.2         19/23.9                

 3/24.70                 4/26.71 2/20.12 1/19.63                                
 22/13.0                 21/17.4 23/19.0 23/03.5                                

 3/22.18                 4/29.98 2/20.09 1/20.75                                
 22/12.7                 21/23.7 23/17.2 23/03.2                                

 3/22.27                         2/20.19 1/19.57                                
 22/12.6                         23/15.7 23/01.7                                

                                 2/23.42 1/19.34                                
                                 23/17.6 23/00.1                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     22/      0/             21/     23/     23/      8/     19/     14/      0/
  8:12.6     0.0          8:23.7  8:17.6  8:00.1  6:59.8  8:23.9  6:08.5     0.0


 ___11__ ___12__ ___13__ ___14__ ___15__ ___16__ ___17__ ___18__ ___19__ ___20__
 4/34.30                                                                        
 14/00.1                                                                        

 5/24.25                                                                        
 17/17.7                                                                        

 5/23.71                                                                        
 18/13.6                                                                        

 5/25.11                                                                        
 18/03.2                                                                        

 5/24.01                                                                        
 19/19.3                                                                        

 5/23.25                                                                        
 19/09.7                                                                        

 5/25.16                                                                        
 19/08.0                                                                        

 5/24.32                                                                        
 19/04.8                                                                        

 5/23.71                                                                        
 19/00.9                                                                        

 5/23.93                                                                        
 20/23.5                                                                        

 5/25.24                                                                        
 20/23.6                                                                        

 5/26.03                                                                        
 20/25.1                                                                        

 5/25.03                                                                        
 20/24.7                                                                        

 5/30.71                                                                        
 19/06.9                                                                        

 5/28.28                                                                        
 19/10.3                                                                        

 6/35.96                                                                        
 19/22.3                                                                        

 5/24.26                                                                        
 19/19.9                                                                        

 5/24.62                                                                        
 19/18.1                                                                        

 5/29.10                                                                        
 19/21.0                                                                        

                                                                                
                                                                                

                                                                                
                                                                                

                                                                                
                                                                                

                                                                                
                                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     19/                                                                        
  8:21.0                                                                        
'''

class TestElevenManPaceData(unittest.TestCase):
 
    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("testfilename", elevenManRaceWithPaceData.split('\n'))
        
    def test_racer3_laptimes(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""] # 23 laps
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[2])
    
    def test_racer12_laptimes(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""] # 23 laps
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[11])

    def test_racer7_laptimes(self):
        expectedLaps = ["254.2", "23.01", "28.15", "23.90", "21.09", "21.30", "22.15", "26.00", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""] # 23 laps
        self.assertEqual(expectedLaps, self.singe_test_race.lapRowsTime[6])


oldBremertonFormat = '''Scoring Software by www.RCScoringPro.com                7:27:45 PM  7/9/2011

                             RankingTestTrack

RankingTestClass A Main                                                        Round# 1, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
                  RankedRacer1    #2      12     6:22.032     30.964           
                  RankedRacer2    #1      10     6:17.466     34.078           
                  RankedRacer3    #3       5     2:43.317     31.628           

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 1/15.27 2/16.03 3/16.80                                                        
 2/38.46 1/33.71 3/38.81                                                        
 3/38.15 2/38.22 1/31.62                                                        
 3/44.80 1/30.96 2/44.17                                                        
 3/39.02 1/31.12 2/31.89                                                        
 2/43.29 1/31.67                                                                
 2/49.39 1/32.09                                                                
 2/37.37 1/32.39                                                                
 2/34.07 1/35.47                                                                
 2/37.60 1/33.41                                                                
         1/32.41                                                                
         1/34.50                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     10/     12/      5/                                                        
  6:17.4  6:22.0  2:43.3 
'''
        
class TestOldBremertonFromat(unittest.TestCase):

    def setUp(self):        
        self.singe_test_race = RCScoringProTXTParser("testfilename", oldBremertonFormat.split('\n'))
        
    def test_headerData(self):
        # RankedRacer1    #2      12     6:22.032     30.964           
        self.assertEqual(self.singe_test_race.raceHeaderData[0], 
                         {"Driver":"RankedRacer1", 
                          "Car#":2, 
                          "Laps":12, 
                          "RaceTime":"6:22.032", 
                          "Fast Lap":"30.964", 
                          "Behind":"",
                          "Final Position":1})
        # RankedRacer2    #1      10     6:17.466     34.078           
        self.assertEqual(self.singe_test_race.raceHeaderData[1], 
                         {"Driver":"RankedRacer2", 
                          "Car#":1, 
                          "Laps":10, 
                          "RaceTime":"6:17.466", 
                          "Fast Lap":"34.078", 
                          "Behind":"",
                          "Final Position":2})


if __name__ == '__main__':
    unittest.main()
    
    
    
