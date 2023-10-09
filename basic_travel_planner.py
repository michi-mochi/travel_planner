#!/usr/bin/env python
# coding: utf-8

# In[25]:


import numpy as np
import requests


# In[26]:


# Enter your Google Maps API key
gmaps_key = ''


# In[27]:


def get_api(source, dest, gmaps_key):
    url ='https://maps.googleapis.com/maps/api/distancematrix/json?'
    r = requests.get(url + 'origins=' + source +
                     '&destinations=' + dest +
                     '&key=' + gmaps_key)
    x = r.json()
    x = dict(x)
    distance = x['rows'][0]['elements'][0]['distance']['value']/1000
    travel_time = x['rows'][0]['elements'][0]['duration']['value']/60
    return [float(distance),round(travel_time,1)]


# In[28]:


#construct a source-destination pair
def construct_source_dest_pair(addresses):
    source_dest_pair = []
    for i in range(0,len(addresses)): # source
        for j in range(i+1,len(addresses)): # destination
            source_dest_pair.append([addresses[i],addresses[j]])
    return source_dest_pair


# In[29]:


#construct lists to store distance & travel time for each pair of locations
def calculate_distance_and_travel_time(source_dest_pair,gmaps_key):
    distance_list=[]
    travel_time_list=[]

    for i in range(0,len(source_dest_pair)):
        stat = []
        stat = get_api(source_dest_pair[i][0],source_dest_pair[i][1],gmaps_key)
        distance_list.append(stat[0])
        travel_time_list.append(stat[1])
    return distance_list,travel_time_list


# In[30]:


def create_distance_matrix(addresses,distance_list):
    distance_matrix=[]
    for i in range(0,len(addresses)):
        temp_matrix = [0] * len(addresses)
        distance_matrix.append(temp_matrix)
    temp_list_row = distance_list.copy()
    for i in range(0,distance_matrix.__len__()):
        # for each source
        for j in range(i+1,distance_matrix.__len__()):
            distance_matrix[i][j] = temp_list_row.pop(0)
    temp_list_col = distance_list.copy()
    for i in range(0,distance_matrix.__len__()):
        # for each source
        for j in range(i+1,distance_matrix.__len__()):
            distance_matrix[j][i] = temp_list_col.pop(0)
    return distance_matrix


# In[31]:


def create_travel_time_matrix(addresses,travel_time_list):
    travel_time_matrix=[]
    for i in range(0,len(addresses)):
        temp_matrix = [0] * len(addresses)
        travel_time_matrix.append(temp_matrix)
    temp_list_row = travel_time_list.copy()
    for i in range(0,travel_time_matrix.__len__()):
        # for each source
        for j in range(i+1,travel_time_matrix.__len__()):
            travel_time_matrix[i][j] = temp_list_row.pop(0)
    temp_list_col = travel_time_list.copy()
    for i in range(0,travel_time_matrix.__len__()):
        # for each source
        for j in range(i+1,travel_time_matrix.__len__()):
            travel_time_matrix[j][i] = temp_list_col.pop(0)
    return travel_time_matrix


# In[464]:


def limit_prioritized_destinations_by_time(travel_time_matrix, distance_matrix, labels, stay_durations, open_times, close_times, time_out_threshold, time_start):
    planned_dest = []
    time_spent = 0
    
    if sum(start_the_day_with) > 0:
    # find destination that we want to start the day with
    # if there are multiple prioritized destinations, find the one we plan to spend most times on
        l = [a for a in range(len(start_the_day_with)) if start_the_day_with[a] == True]
        i = l[[stay_durations[i] for i in l].index(max([stay_durations[i] for i in l]))]
 #       i = start_the_day_with.index(True)
    else:
    # else we start the day with a destination that is furthest away from the hotel
        i = distance_matrix[0].index(sorted(distance_matrix[0])[len(labels)-1])
    print(labels[0], ' -> ', labels[i], '|| hours of operations: ', open_times[i], ':00 to ', 
      close_times[i], ':00 || distance:', distance_matrix[0][i], 'km || travels time:', 
      travel_time_matrix[0][i], 'min || arrival time: ', int(time_start+(travel_time_matrix[0][i]//60)), ':', 
      int(travel_time_matrix[0][i]%60), '|| stay duration:', stay_durations[i], 'hours || daily time lapse: ', 
      int((travel_time_matrix[0][i] + stay_durations[i]*60)//60), 'hours',
      int((travel_time_matrix[0][i] + stay_durations[i]*60)%60), 'minutes')
    planned_dest.append(i)
    time_spent += travel_time_matrix[0][i] + stay_durations[i]*60
    
    # adding more destinations into the day
    while (time_spent < time_out_threshold * 0.6) and len(labels)>1:
        t = 1
        j = distance_matrix[i].index(sorted(distance_matrix[i])[t])
        
        
        while t < len(labels)-1 and ((j in planned_dest) or j ==0 or (time_start+(time_spent + travel_time_matrix[i][j])/60 <= open_times[j]) or ((time_start*60+ time_spent + travel_time_matrix[i][j] + stay_durations[j]*60) >= close_times[j]*60)):
            t += 1
            j = distance_matrix[i].index(sorted(distance_matrix[i])[t])
            
        if j == 0:
            break

        # if no destination is available
        if (time_start+(time_spent + travel_time_matrix[i][j])/60 <= open_times[j]) or ((time_start*60+ time_spent + travel_time_matrix[i][j] + stay_durations[j]*60) >= close_times[j]*60):
            print('Free time or rest early for the day!')
            break
        # if time does not exceed daily limit including route back to the hotel    
        elif time_spent < time_out_threshold - travel_time_matrix[i][j] - stay_durations[j]*60 - travel_time_matrix[i][j]: 
            print(labels[i], ' -> ', labels[j], '|| hours of operations: ', open_times[j], ':00 to ', 
                  close_times[j], ':00 || distance:', distance_matrix[i][j],
                  'km || travels time:', travel_time_matrix[i][j], 'min || arrival time: ', 
                  int(time_start+((time_spent+ travel_time_matrix[i][j])//60)), ':', 
                  int((time_spent + travel_time_matrix[i][j])%60), '|| stay duration:',
                  stay_durations[j], 'hours || daily time lapse: ', 
                  int((time_spent+travel_time_matrix[i][j] + stay_durations[j]*60)//60), 'hours',
                  int((time_spent+travel_time_matrix[i][j] + stay_durations[j]*60)%60), 'minutes')
            time_spent += travel_time_matrix[i][j] + stay_durations[j]*60
            planned_dest.append(j)
            i = j

        # route back to the hotel
    print(labels[i], ' -> ', labels[0],'|| distance:', distance_matrix[i][0],
              'km || travels time:', travel_time_matrix[i][0],
              'min || arrival time: ', int(time_start+((time_spent+ travel_time_matrix[i][0])//60)), ':', 
              int((time_spent + travel_time_matrix[i][0])%60), '|| daily time lapse: ', 
              int((time_spent+travel_time_matrix[i][0] )//60), 'hours',
              int((time_spent+travel_time_matrix[i][0])%60), 'minutes')
    return planned_dest
    

            

        


# In[366]:


def drop_destinations(planned_dest, labels, addresses, stay_durations, open_times, close_times, start_the_day_with):
    sorted_planned_list = sorted(planned_dest, reverse = True)

    for index in sorted_planned_list:
        labels.pop(index)
        addresses.pop(index)
        stay_durations.pop(index)
        open_times.pop(index)
        close_times.pop(index)
        start_the_day_with.pop(index)
    return labels, addresses, stay_durations, open_times, close_times, start_the_day_with


# In[466]:


# Example 1: Sedona

addresses = [
    '55 Sunridge Cir, Sedona, AZ 86351',
    '171B Forest Rd, Flagstaff, AZ 86001',
    '2650 Pueblo Dr, Sedona, AZ 86336',
    '780 Chapel Rd, Sedona, AZ 86336',
    '160 Portal Ln, Sedona, AZ 86336',
    '500 Back O Beyond Rd, Sedona, AZ 86336',
    '4999 AZ-179, Sedona, AZ 86351',
    "Devil's Bridge Trail, Sedona, AZ 86336",
    'Long Canyon Trail, Sedona, AZ 86336',
    'Meteor Crater Rd, Winslow, AZ 86047'    
]

labels = [
    'Hotel',
    'Lava River Cave',
    'Amitabha Stupa & Peace Park',
    'Sedona Holy Cross Chapel',
    'Tlaquepaque Arts and Crafts Village',
    'Catherdral Rock',
    'Bell Rock',
    "Devil's Bridge Trail",
    'Subway Cave',
    'Meteor Crate'
]

stay_durations = [
    0,
    2,
    1,
    0.75,
    2,
    5,
    1.5,
    4,
    6,
    2
]

open_times = [
    0,
    6,
    0,
    9,
    10,
    6,
    6,
    6,
    6,
    8
    
]
    
close_times = [
    24,
    18,
    24,
    17,
    17,
    18,
    18,
    18,
    18,
    17
]

start_the_day_with = [
    False,
    False,
    False,
    False,
    False,
    True,
    False,
    True,
    True,
    False
]

time_out_threshold = 660  
time_start = 9 # time to start the day


# In[469]:


# Example 2: Portland
addresses = [
    '11942 NE Sandy Blvd, Portland, OR 97220',
    '700 SW 6th Ave, Portland, OR 97204',
    '1535 SW Park Ave, Portland, OR 97201',
    '1126 SW Alder St, Portland, OR 97205',
    '611 SW Kingston Ave, Portland, OR 97205',
    '50000 Historic Columbia River Hwy, Bridal Veil, OR 97010',
    '700 SW 5th Ave, Portland, OR 97204',
    '450 NW 257th Way, Troutdale, OR 97060'
    
]

labels = [
    'Hotel',
    'Pioneer Square',
    'Donut Tour',
    "S'more Company",
    'Japanese Garden',
    'Columbia River Gorge Waterfalls Tour',
    'LV Shopping',
    'Columbia Gorge Outlets'

]

stay_durations = [
    0,
    2.5,
    2,
    0.5,
    6,
    8,
    1,
    4
]

open_times = [
    0,
    10,
    9,
    14,
    10,
    7,
    11,
    10
    
]
    
close_times = [
    24,
    19,
    14,
    23,
    16,
    18,
    19,
    20    
]

start_the_day_with = [
    False,
    False,
    False,
    False,
    True,
    True,
    False,
    False
]

time_start = 10 # time to start the day
time_out_threshold = 600 


# In[470]:


itinerary = []
x = 1

while len(labels)>1:
    print('Day', x, ':')
    source_dest_pair = construct_source_dest_pair(addresses)
    distance_list,travel_time_list = calculate_distance_and_travel_time(source_dest_pair,gmaps_key)
    distance_matrix = create_distance_matrix(addresses,distance_list)
    travel_time_matrix = create_travel_time_matrix(addresses,travel_time_list)
    planned_dest = limit_prioritized_destinations_by_time(travel_time_matrix, distance_matrix, labels, stay_durations, open_times, close_times, time_out_threshold, time_start)
    itinerary.append([labels[x] for x in planned_dest])
    labels, addresses, stay_durations, open_times, close_times, start_the_day_with = drop_destinations(planned_dest, labels, addresses, stay_durations, open_times, close_times, start_the_day_with)
    x += 1


# In[472]:


print(itinerary)


# In[ ]:




