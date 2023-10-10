# -*- coding: utf-8 -*-

import datetime


#from: https://stackoverflow.com/questions/12691551/add-n-business-days-to-a-given-date-ignoring-holidays-and-weekends-in-python
def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date

def get_next_date(date):
    return date_by_adding_business_days(date, 1)