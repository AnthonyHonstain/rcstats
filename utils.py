'''
Created on Oct 27, 2012

@author: Anthony Honstain

General utility functions used throughout the site.

Particularly for time and other special formating issues. 

http://docs.python.org/2/library/datetime.html#datetime.datetime.strptime
'''
import time
import pytz
from django.conf import settings


def formated_local_time_for_orm():
    '''
    Return the local time in a format needed to insert into the DB.
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def formated_orm_time_for_user(orm_time):
    """
    Take the datetime object and generate the string to display to users.
    """
    return orm_time.strftime('%a, %d %b %Y')

def format_racetime_for_user(orm_time):
    return orm_time.strftime('%M:%S.%f')

def format_date_for_user(orm_date):
    '''
    Present the date in the system format time, especially for dates that
    need to be extracted and operated on prior to presenting them to the user.
    They will come out of the DB in UTC, and we assume they have been uploaded
    in the system time zone.
    '''
    tmz = pytz.timezone(settings.TIME_ZONE)
    return orm_date.astimezone(tmz).strftime("%c")

def format_main_event_for_user(race_detail):
    '''
    Convert the main event information into a format suitable for user.
    '''
    class_name = race_detail.racedata
    # Include main event information in class name
    if race_detail.mainevent >= 1:
        class_name += " " + race_detail.maineventparsed
    return class_name