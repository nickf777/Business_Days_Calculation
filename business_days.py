# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:35:25 2022

@author: fallern
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 09:55:59 2022
@author: Nickf
"""

import pandas as pd
import numpy as np
from datetime import time
import requests
import bs4
import unidecode
from business_duration import businessDuration
from itertools import repeat

start_time = time(9,0,0)
end_time = time(17,0,0)
weekend_list = [5,6]
unit_hour='hour'

test_csv = "xyz.csv"

def get_holidays():
    url = 'https://www.tpsgc-pwgsc.gc.ca/remuneration-compensation/services-pension-services/pension/joursferies-stathol-eng.html'
    
    result = requests.get(url)
    soup = bs4.BeautifulSoup(result.text, 'lxml')
    
    holiday_table = soup.select('td')
    
    holiday_names = []
    holiday_dates = []
    
    for i in range(0,len(holiday_table)):
        if i % 2 == 0:
            holiday_names.append(holiday_table[i].getText())
        else:
            holiday_dates.append(unidecode.unidecode((holiday_table[i].getText())))
          
    #Creates a dataframe of holidays
    '''
    holiday_dict = dict(zip(holiday_dates, holiday_names))
    dct = {k:[v] for k,v in holiday_dict.items()}
    df_wide = pd.DataFrame(dct)
    df_wide = df_wide.reset_index()
    df = pd.melt(df_wide, value_vars = holiday_names)
    df = df.rename({'variable':'holiday','value':'date'}, axis = 1)
    '''
    
    holiday_array = np.array(holiday_dates)
    holiday_array = pd.to_datetime(holiday_array)
    holiday_array = holiday_array.values.astype('datetime64[D]')
    
    return holiday_array

def get_working_days(csv, holiday):
    raw_data = pd.read_csv(csv)
    data = raw_data.copy()
    
    date1 =  pd.to_datetime(data['StartDate'], format = '%Y-%m-%d %H:%M:%S')
    date2 = pd.to_datetime(data['EndDate'], format = '%Y-%m-%d %H:%M:%S')
    
    date1 = date1.values.astype('M8[D]')
    date2 = date2.values.astype('M8[D]')
    
    working_days = np.busday_count(date1, date2, weekmask = '1111100', holidays = holiday)
    
    return working_days

def get_working_hours(csv,start_time,end_time,holiday):
    raw_data = pd.read_csv(csv)
    data = raw_data.copy()
    
    date1 = pd.to_datetime(data['StartDate'], format = '%Y-%m-%d %H:%M:%S')
    date2 = pd.to_datetime(data['EndDate'], format = '%Y-%m-%d %H:%M:%S')

    
    holiday_list = list(holiday)
    
    working_hours = list(map(businessDuration,date1, date2,repeat(start_time),repeat(end_time),repeat(weekend_list),repeat(holiday_list),repeat(unit_hour)))
    
    return working_hours

def bus_data_write(csv):
    data = pd.read_csv(csv)
    holidays = get_holidays()
    
    data['working_days'] = get_working_days(csv, holidays)
    data['working_hours'] = get_working_hours(csv,start_time,end_time,holidays)
    
    data.to_csv(f'{csv}_bus_time_elapsed.csv')
    
bus_data_write(test_csv)
