'''
Created on Jul 19, 2012

@author: Anthony Honstain
'''


class SingleRace(object):
    """
    SingleRace contains the following race information:
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
    
    """
    def __init__(self):
        '''
        Constructor - Will initialize all the required properties.
        '''
        self.filename = None
    
        self.date = None
        self.trackName = None
        self.raceClass = None
        self.roundNumber = None
        self.raceNumber = None
        self.mainEvent = None
        self.mainEventRoundNum = None
        self.mainEventParsed = None
        
        self.raceHeaderData = [] # List of Dictionaries
        self.lapRowsTime = [] # List of Lists
        self.lapRowsPosition = []

    def __str__(self):
        return self.trackName + " | " +\
            self.raceClass + " | " +\
            self.roundNumber + " | " +\
            self.raceNumber + " | " +\
            self.date