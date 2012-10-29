'''
Created on Oct 27, 2012

@author: Anthony Honstain

General utility functions used throughout the site.

Particularly for time and other special formating issues. 
'''
import time

def formated_local_time_for_orm():
    '''
    Return the local time in a format needed to insert into the DB.
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def format_main_event_for_user(race_detail):
    '''
    Convert the main event information into a format suitable for user.
    '''
    class_name = race_detail.racedata
    # Include main event information in class name
    if race_detail.mainevent >= 1:
        class_name += " " + race_detail.maineventparsed
    return class_name