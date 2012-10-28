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