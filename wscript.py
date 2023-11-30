import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objs as go
import plotly.express as px
import math
import requests
from io import StringIO

url="https://radwatch.berkeley.edu/test/tmp/Station.csv"
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

s=requests.get(url, headers=header).text
stations=pd.read_csv(StringIO(s))
import listofstations
def grabFile(nickname=""):
    try:
      url=listofstations.stationsdict[nickname] #nickname is used in URL to source CSV file for location.
      locationCSV =requests.get(url, headers=header).text #grabs the CSV file for location
      locationDF =pd.read_csv(StringIO(locationCSV)) #reads the CSV file into Pandas Dataframe.
    except: #if necessary tasks result in an error, the location is skipped
        print('FILE NOT FOUND!')
        raise Exception("Error Occured [Skipped]")
    else: #if the tasks were successful, it will do the following
        return locationDF
stationDFs = [] #this variable will be used to store Pandas Dataframes for each station.
areaNames = [] #this variable will be used to store the names of each station.
continents = []

for areas in range(1,len(stations.index)): #loop over the length of (# of locations in) the DataFrame
    try: #this attemps to complete necessary tasks for the location
        nickname = stations['nickname'][areas] #grab nickname from the 'nickname' column for location.
        name = stations['Name'][areas] #grabs the full name of the location
        geo = stations['timezone'][areas]
        locationDF = grabFile(nickname)
    except: #if necessary tasks result in an error, the location is skipped
        print('error occured, df for ' + nickname + ' [skipped]')
        continue
    else: #if the tasks were successful, it will do the following
        stationDFs.append(locationDF) #add dataframe to list
        areaNames.append(name) #add full name of the location to list
        continents.append(geo)
        print('done.' + nickname)
print('\n\n** complete. **')
def a_week_back(dataframe):
    endUnix = dataframe["deviceTime_unix"][(len(dataframe)-1)]
    idealstartUnix = endUnix - 604800
    for i in range(len(dataframe)):
        if(dataframe["deviceTime_unix"][i]>=idealstartUnix):
            closestfit = i
            break
    return closestfit

def weekly_ave(dataframe, sumover, indicator):
    splice = dataframe.iloc[(a_week_back(dataframe)):len(dataframe),:]
    if (indicator == 0):
        weekly_ave = splice[sumover].sum()/(len(splice)) 
        return weekly_ave
    else:
        weekly_ave = (math.sqrt(splice[sumover].sum()))/(len(splice.to_numpy())*5)
        return weekly_ave

#locations and location_dfs are both lists
def create_bar_df(locations,location_dfs,sumover):
    weeklyave = []
    error = []
    displaycontinents = []
    for x in range(len(location_dfs)):
        weeklyave.append(weekly_ave(location_dfs[x],sumover,0))
        error.append(weekly_ave(location_dfs[x],sumover,1))
        displaycontinents.append(continents[x][0:continents[x].index("/")])
    df_data = {"locations" : locations, sumover + "_ave" : weeklyave, "error" : error, "continents" : displaycontinents}
    final_df = pd.DataFrame(df_data)
    final_df = final_df.sort_values(by=['continents'])
    return final_df

goal = create_bar_df(areaNames, stationDFs, "cpm")
fig = px.bar(goal, x=goal["locations"], y = goal["cpm_ave"], 
             title="Weekly CPM averages at different locations",  
             error_y=goal["error"],
             labels=dict(locations="Locations", cpm_ave="Average Weekly CPM", continents = "Regions"),
            color = goal["continents"], hover_data = {"continents" : False})

fig.update_traces(hovertemplate = "<b>%{x}</b>"+"<br>Region: "+goal["continents"] +"</br>Average CPM (counts per minute) : %{y}"
                    +"<br>Data collected from <i></i> to <i></i></br>")
fig.update_layout(showlegend=True)
plotly.offline.plot(fig, filename=r'')
