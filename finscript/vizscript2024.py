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
header={
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}
s=requests.get(url, headers=header).text
stations=pd.read_csv(StringIO(s))
import listofstations
def grabFile(nickname=""):
    try:
        url=listofstations.stationsdict[nickname]
        locationCSV=requests.get(url, headers=header).text
        locationDF=pd.read_csv(StringIO(locationCSV))
    except:
        print('FILE NOT FOUND!')
        raise Exception("Error Occured [Skipped]")
    else: #if the tasks were successful, it will do the following
        return locationDF
stationDFs = [] 
areaNames = [] 
continents = []
for areas in range(1,len(stations.index)):
    try:
        nickname = stations['nickname'][areas] 
        name = stations['Name'][areas] 
        geo = stations['timezone'][areas]
        locationDF = grabFile(nickname)
    except: 
        print('error occured, df for ' + nickname + ' [skipped]')
        continue
    else: 
        stationDFs.append(locationDF) 
        areaNames.append(name) 
        continents.append(geo)
        print('done.' + nickname)
print('\n\n** complete. **')
sampling_start_date = []
sampling_end_date = []

def a_week_back(dataframe, nstations):
    endUnix = dataframe["deviceTime_unix"][(len(dataframe)-1)]
    idealstartUnix = endUnix - 604800
    for i in range(len(dataframe)):
        if(dataframe["deviceTime_unix"][i]>=idealstartUnix):
            closestfit = i
            break
    if len(sampling_start_date)<nstations and len(sampling_end_date)<nstations:
        sampling_start_date.append(dataframe["deviceTime_utc"][i] + "UTC")
        sampling_end_date.append(dataframe["deviceTime_utc"][(len(dataframe)-1)] + "UTC")
    return closestfit
def weekly_ave(dataframe, sumover, indicator, nstations):
    splice = dataframe.iloc[(a_week_back(dataframe,nstations)):len(dataframe),:]
    if (indicator == 0):
        weekly_ave = splice[sumover].sum()/(len(splice)) 
        return weekly_ave
    else:
        weekly_ave = (math.sqrt(splice[sumover].sum()))/(len(splice.to_numpy())*5)
        return weekly_ave
def create_bar_df(locations,location_dfs,sumover):
    weeklyave = []
    error = []
    displaycontinents = []
    nstations = len(location_dfs)
    for x in range(nstations):
        weeklyave.append(weekly_ave(location_dfs[x],sumover,0,nstations))
        error.append(weekly_ave(location_dfs[x],sumover,1,nstations))
        displaycontinents.append(continents[x][0:continents[x].index("/")])
    df_data = {"locations" : locations, sumover + "_ave" : weeklyave, "error" : error, "continents" : displaycontinents, "samplingstarts"  : sampling_start_date , "samplingends" : sampling_end_date}
    final_df = pd.DataFrame(df_data)
    return final_df

plot_df = create_bar_df(areaNames, stationDFs, "cpm")
fig = px.bar(plot_df, x="locations", y = "cpm_ave",
              title="Weekly CPM averages at different locations",
              error_y="error",
              color = "continents",
              color_discrete_map={'America': 'red', 'Asia': 'green', 'Europe':'royalblue'}) #this is just aesthetics
fig.update_traces(hovertemplate = "<b>%{x}</b></br>Average CPM (counts per minute) : %{y}"
                   +"<br>Data collected from <i>"+plot_df["samplingstarts"]+"</i> to <i>"+plot_df["samplingends"]+"</i></br><extra></extra>") 
fig.update_layout(xaxis_title="Location", yaxis_title="Average CPM (counts per minute)",legend_title = "Regions")
plotly.io.to_html(fig)
plotly.offline.plot(fig, filename=r'allstationscpm.html')



