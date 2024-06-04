#!/usr/bin/env python
# coding: utf-8

# # Creating subsets

# ### Importings

# In[16]:


import pandas as pd
import matplotlib.pyplot as pyplot
import datetime
import os, shutil


# We chose to use the original dataset (before cleaning) when finding the original distribution of values for the different parameters. This is because even though a taxi-trip is deleted during the cleaning, it doesn't mean that it is something wrong with the trip, just the GPS. So if for example a lot of the trips with a spesific value on one parameter is deleted (due to unlucky GPS): we still want the distribution to be the same in the subsets, to be as close as possible to reality.

# In[17]:


original_data = pd.read_csv('train.csv')
cleaned_data = pd.read_csv('subset-2500-7-percent.csv')


# ### Geographical cleaning of original data

# In[18]:


#Set max and min coordinates for latitude and longitude
MAX_LON = -8.45
MIN_LON = -8.72
MAX_LAT = 41.26
MIN_LAT = 41.07

# Will choose traces that are within a given rectangle of the city

indexes_to_delete = []

for index, row in original_data.iterrows():
    trace_id = row["TRIP_ID"] 

    trace = row["POLYLINE"][2:-2].split("],[")
    if(trace[0]==''):
        indexes_to_delete.append(index)
    else:
        # If trace are outside bounded rectangle: remove row
        for coordinate in trace:
            lon, lat = list(map(float, coordinate.split(",")))

            # Outside bounded rectangle
            if ( not ( MIN_LAT <= lat <= MAX_LAT )) or ( not ( MIN_LON <= lon <= MAX_LON )):
                indexes_to_delete.append(index)
                break
      
original_data.drop(indexes_to_delete, inplace=True)


# ### Some extra cleaning before the subset creation

# In[19]:


#cleaned_data = cleaned_data[cleaned_data['MISSING_DATA']!=True]
#cleaned_data.drop(['ORIGIN_CALL', 'ORIGIN_STAND', 'TAXI_ID', 'MISSING_DATA', 'DAY_TYPE'], axis=1, inplace=True)


# In[20]:


original_length = len(original_data)
subset_length = 1000
#7500, 5000, 2500, 2000, 1500, 1000, 500, (300), 200, 100, 50
print(original_length)


# # Create subsets and check if they are good enough

# # CALL_TYPE

# ### Saving the distribution in the original dataset

# In[21]:


#finding the number of rows of each call type (A, B, C) in the original dataset
original_call_type_a_percentage = (len(original_data[original_data['CALL_TYPE']=='A'])/original_length)*100
original_call_type_b_percentage = (len(original_data[original_data['CALL_TYPE']=='B'])/original_length)*100
original_call_type_c_percentage = (len(original_data[original_data['CALL_TYPE']=='C'])/original_length)*100

print(original_call_type_a_percentage)
print(original_call_type_b_percentage)
print(original_call_type_c_percentage)



# ### Creating method to check wheter a subset has a similar distribution as the original dataset

# In[22]:


def call_type_accepted(subset_call_type_a_percentage, subset_call_type_b_percentage, subset_call_type_c_percentage):
    if abs(original_call_type_a_percentage - subset_call_type_a_percentage) <= (original_call_type_a_percentage*0.07):
        if abs(original_call_type_b_percentage - subset_call_type_b_percentage) <= (original_call_type_b_percentage*0.07):
            if abs(original_call_type_c_percentage - subset_call_type_c_percentage) <= (original_call_type_c_percentage*0.07):
                return True
    return False


# # TIMESTAMP

# ### Creating method to get the info from (hours, weekdays and months) the timestamps 

# In[23]:


def get_info_from_timestamps(subset):
    hours_dict = {
        0:0,
        1:0,
        2:0,
        3:0,
        4:0,
        5:0,
        6:0,
        7:0,
        8:0,
        9:0,
        10:0,
        11:0,
        12:0,
        13:0,
        14:0,
        15:0,
        16:0,
        17:0,
        18:0,
        19:0,
        20:0,
        21:0,
        22:0,
        23:0
    }
    days_dict={
        "Monday":0,
        "Tuesday":0,
        "Wednesday":0,
        "Thursday":0,
        "Friday":0,
        "Saturday":0,
        "Sunday":0
    }
    months_dict={
        1:0,
        2:0,
        3:0,
        4:0,
        5:0,
        6:0,
        7:0,
        8:0,
        9:0,
        10:0,
        11:0,
        12:0
    }
    
    for row in subset['TIMESTAMP']:
        time = datetime.datetime.fromtimestamp(row)
        hours_dict[time.hour]+=1
        days_dict[time.strftime("%A")]+=1
        months_dict[time.month]+=1
    return hours_dict, days_dict, months_dict


# ### Saving the timestamp-info from the original data

# In[24]:


#finding the number of rows of each hour, weekday and month from timestamp in the original dataset
original_hours, original_weekdays, original_months = get_info_from_timestamps(original_data)

print(original_hours)
print(original_weekdays)
print(original_months)


# In[25]:


#Convert original timestamps-dicts into percentage dicts
original_hours_percentage_dict = {}
for hour in original_hours:
    original_hours_percentage_dict[hour] = (original_hours[hour]/original_length)*100

original_weekdays_percentage_dict = {}
for weekday in original_weekdays:
    original_weekdays_percentage_dict[weekday] = (original_weekdays[weekday]/original_length)*100

original_months_percentage_dict = {}
for month in original_months:
    original_months_percentage_dict[month] = (original_months[month]/original_length)*100

print(original_hours_percentage_dict)
print(original_weekdays_percentage_dict)
print(original_months_percentage_dict)


# ### Creating functions for checking if hours, weekdays and months are evenly distributed compared to original dataset

# In[26]:


def weekdays_accepted(subset_weekdays_dict):
    for weekday in subset_weekdays_dict:
        subset_percentage = (subset_weekdays_dict[weekday]/subset_length)*100
        if abs(original_weekdays_percentage_dict[weekday]-subset_percentage)>(original_weekdays_percentage_dict[weekday]*0.07):
            return False
    return True
            
def months_accepted(subset_months_dict):
    for month in subset_months_dict:
        subset_percentage = (subset_months_dict[month]/subset_length)*100
        if abs(original_months_percentage_dict[month]-subset_percentage)>(original_months_percentage_dict[month]*0.07):
            return False
    return True

def hours_accepted(subset_hours_dict):
    for hour in subset_hours_dict:
        subset_percentage = (subset_hours_dict[hour]/subset_length)*100
        if abs(original_hours_percentage_dict[hour]-subset_percentage)>(original_hours_percentage_dict[hour]*0.07):
            return False
    return True


# ###

# # Methods to print histograms

# ### CALL_TYPE:

# In[27]:


def print_histogram(column, subset):
    data_sorted = cleaned_data.sort_values(by=column)
    subset_sorted = subset.sort_values(by=column)

    pyplot.hist(data_sorted[column], bins='auto')
    pyplot.xlabel(column)
    pyplot.ylabel('number of rows')
    pyplot.title('Original dataset. ' + column)
    pyplot.show()

    pyplot.hist(subset_sorted[column], bins='auto')
    pyplot.xlabel(column)
    pyplot.ylabel('number of rows')
    pyplot.title('Subset, ' + column)
    pyplot.show()


# ### TIMESTAMP

# In[28]:


def print_histogram_timestamps(hours_dict, days_dict, months_dict):
    keys_hours = list(hours_dict.keys())
    values_hours = list(hours_dict.values())
    pyplot.bar(keys_hours, values_hours)
    pyplot.title("HOURS")
    pyplot.show()

    keys_hours = list(original_hours.keys())
    values_hours = list(original_hours.values())
    pyplot.bar(keys_hours, values_hours)
    pyplot.title("ORIGINAL HOURS")
    pyplot.show()

    keys_days = list(days_dict.keys())
    values_days = list(days_dict.values())
    pyplot.bar(keys_days, values_days)
    pyplot.title("DAYS")
    pyplot.show()

    keys_days = list(original_weekdays.keys())
    values_days = list(original_weekdays.values())
    pyplot.bar(keys_days, values_days)
    pyplot.title("ORIGINAL DAYS")
    pyplot.show()

    keys_months = list(months_dict.keys())
    values_months = list(months_dict.values())
    pyplot.bar(keys_months, values_months)
    pyplot.title("MONTHS")
    pyplot.show()

    keys_months = list(original_months.keys())
    values_months = list(original_months.values())
    pyplot.bar(keys_months, values_months)
    pyplot.title("ORIGINAL MONTHS")
    pyplot.show()


# ## Create subset
# Chose a random subset of the chosen size (subset_length), and check if the distribution is similar enough. Try again until a solution is found.

# In[29]:


subset_ok = False
counter = 1

while subset_ok==False:
    #create subset, from the cleaned data
    subset = cleaned_data.sample(n=subset_length)

    #CALL_TYPE
    subset_call_type_a_percentage = (len(subset[subset['CALL_TYPE']=='A'])/subset_length)*100
    subset_call_type_b_percentage = (len(subset[subset['CALL_TYPE']=='B'])/subset_length)*100
    subset_call_type_c_percentage = (len(subset[subset['CALL_TYPE']=='C'])/subset_length)*100

    #HOURS; WEEKDAYS; MONTHS
    subset_hours_dict, subset_weekdays_dict, subset_months_dict = get_info_from_timestamps(subset)

    if months_accepted(subset_months_dict):
        if hours_accepted(subset_hours_dict):
            if weekdays_accepted(subset_weekdays_dict):
                if call_type_accepted(subset_call_type_a_percentage, subset_call_type_b_percentage, subset_call_type_c_percentage):
                    print(counter)
                    subset_ok=True
                    subset.to_csv('subset-1000-7-percent.csv', index=False)
                    print_histogram("CALL_TYPE", subset)
                    print_histogram_timestamps(subset_hours_dict, subset_weekdays_dict, subset_months_dict)
    counter+=1


# In[ ]:


import csv

input_file = "subset-1000-7-percent.csv"
output_file = "sorted-subset-1000-7.csv"


# Read the CSV file into a list of dictionaries
with open(input_file, 'r') as csv_input:
    reader = csv.DictReader(csv_input)
    data = [row for row in reader]

# Sort the data based on the 'INDEX' field
sorted_data = sorted(data, key=lambda x: int(x['INDEX']))

# Write the sorted data to a new CSV file
with open(output_file, 'w', newline='') as csv_output:
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted_data)

