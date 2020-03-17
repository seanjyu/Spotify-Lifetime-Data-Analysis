# PLOTTING THE LIFETIME OF SONGS ON THE BILLBOARD HOT 100 WITHIN A GIVEN PERIOD
# NOTE:  CHANGE PLOT DATES ON LINE 206 - 207
#        CHANGE PLOT X-AXIS RANGE ON LINE 287

import pandas as pd
import datetime as dt
import time
import cufflinks as cf
import plotly as py
import plotly.graph_objs as go
import numpy as np
from itertools import repeat
from plotly.offline import init_notebook_mode, iplot
import plotly.io as pio
import dash_core_components as dcc
import warnings
init_notebook_mode()

# Choose Rankings
rankLow = 1
rankHigh = 1

# Function to plot data for given year
def plotbbdata(rankLow,rankHigh,startPeriod,endPeriod):
    
    # function for converting time from string to datetime FROM STRING TO DATETIME
    def readTime(ti):
        read = (dt.datetime.strptime(ti, "%Y-%m-%d")).date()
        return read

    # read data from csv file
    allData = pd.read_csv("billboardData.csv")
    rankData = allData[(allData["rank"]>=rankLow) & (allData["rank"]<=rankHigh)]
    rankData = rankData.drop_duplicates(subset=["songName","artistName"])
    rankData = rankData.reset_index(drop=True)

    # select data within the given period
    for ind in range(0, int(len(rankData))):
        i = rankData.index.get_loc(ind)
        dateSearch = readTime(rankData.iloc[i]["date"])
        if readTime(startPeriod) <= dateSearch < readTime(endPeriod):
            continue
        else:
            rankData.drop(rankData.index[i], inplace=True)
    rankData = rankData.reset_index(drop=True)

    # plot all songs in rank data
    allycols=list(range(len(rankData)))
    ally=pd.DataFrame()
    allx=[]
    aglastx=[]
    traces=[]
    meanx=0
    for j in range(len(rankData)):
        chooseSong = rankData["songName"][j]
        chooseArtist = rankData["artistName"][j]

        # search data for song
        song = allData.loc[(allData["songName"]==chooseSong)
                            & (allData["artistName"]==chooseArtist)]

        # get y values (song rank)
        y = song["rank"].tolist()

        # get x values (date in datetime format)
        songDate = song["date"].tolist()

        # for every date, read as date time and append to list
        x = []
        
        for i in range(len(songDate)):
            dateT = readTime(songDate[i])
            x.append(dateT)
        
        # normalize all data by date ranked 
        xabs = [0]
        
        for i in range(len(songDate)-1):
            div=int((x[i+1]-x[i]).days/7)
            if div != 1:
                xabs1=list(range(int(div)))
                a=int((x[i]-x[0]).days/7)
                xabs1=[str(z+a+1) for z in xabs1]
                xabs=xabs+xabs1
                for n in range(div-1):
                    y.insert(i+1,'Nan')
                     
            else:
                xabs1 = str(int((x[i+1]-x[0]).days/7))
                xabs.append(xabs1)

        lastx=xabs[-1]
        aglastx.append(lastx)
        
                                  
        # aggregate x
        allx.append(xabs)
        
        
        # create array with all song rankings (ally)
        ydf=pd.DataFrame(y)
        ally=pd.concat([ally,ydf],axis=1) 
        songtrace=(go.Scatter(
                            visible=False,
                            x= xabs,
                            y= y,
                            mode = 'lines',
                            name = chooseSong,
                            opacity=0.35
                            ))
        traces.append(songtrace)

    xabs2=np.array(aglastx).astype(np.float)
    meanx=np.nanmean(xabs2)
    meanxtrace=(go.Scatter(
                            visible=False,
                            x=[meanx,meanx],
                            y=[0,100],
                            mode = 'lines',
                            name ='Average Number of Weeks on Charts'))                     
    traces.append(meanxtrace)              
    # get sd and mean of each week
    meany=[]
    ysd=[]
    for k in range(len(ally)):
        row=np.array(list(ally.iloc[k,:])).astype(np.float)
        if len(row)>=1:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
            mean=np.nanmean(row)
        else:
            mean=float('nan')
        sd=np.nanstd(row)
        meany.append(mean)
        ysd.append(sd)

    # find maximum amount of weeks a song has been on the charts       
    maxx=max(allx)

    # get 1sd plus mean and 1sd minus mean    
    p1sd=np.add(meany,ysd)
    m1sd=np.subtract(meany,ysd)

    # limit p1sd and m1sd values within 0 to 100  
    for m in range(len(m1sd)):
        if m1sd[m]<0:
            m1sd[m]=0

    for n in range(len(m1sd)):
        if p1sd[n]>100:
            p1sd[n]=100

    # if exists splice average and sd plots where sd=0 (after this point only one song is ranked)
    if 0 in ysd:
        stop=ysd.index(0)
    else:
        stop=len(ysd)+1
        
    maxx1=maxx[:stop]
    m1sd1=m1sd[:stop]
    p1sd1=p1sd[:stop]
    meany1=meany[:stop]
    
    # average and SD
    avgtrace=(go.Scatter(
                            visible=False,
                            x= maxx1,
                            y= meany1,
                            mode = 'lines+markers',
                            name = 'Average per Week',    
                            ))
    traces.append(avgtrace)
    topsd=(go.Scatter(
                            visible=False,
                            x=maxx1,
                            y=m1sd1,
                            fill='tonexty',
                            fillcolor='rgba(0,100,80,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            showlegend=False,
                            name='1 Sd',))
    traces.append(topsd)
    botsd=(go.Scatter(
                            visible=False,
                            x=maxx1,
                            y=p1sd1,
                            fill='tonexty',
                            fillcolor='rgba(0,100,80,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            showlegend=False,
                            name='1 Sd',))
    traces.append(botsd)
    #output of function are traces all turned off
    return traces

# function for converting time from string to datetime
def readTime(ti):
        read = (dt.datetime.strptime(ti, "%Y-%m-%d")).date()
        return read
# function for rereading datetime    
def rereadTime(ti):
    reread = str(ti)
    read = (dt.datetime.strptime(reread, "%Y-%m-%d")).date()
    return read

# increments time by a year
def incrementTime(ti):
    return rereadTime(ti) + dt.timedelta(days=365)

# choose dates to get plots
startdate="2012-01-01"
enddate="2014-01-01"

# turn dates into date time
date=startdate
readenddate=readTime(enddate)

# plot for each year
plots=[]
plotnum=[]
years=[str(readTime(date).year)]
while readTime(date)<readenddate:
    datep1=incrementTime(readTime(date))
    plot1=plotbbdata(1,1,str(date),str(datep1))
    plotnum1=len(plot1)
    plots=plots+plot1
    plotnum.append(plotnum1)
    date=str(incrementTime(readTime(date)))
    years.append(str(int(datep1.year)+1))
fig = go.Figure(plots)
nyears=len(plotnum)
steps=[]
count=0
# turn on plots for single slider
for i in range(nyears):
    # hide all traces (reset every year)
    step = dict(
        method = 'restyle',  
        args = ['visible', [False] * len(plots)],
        label=years[i],
    )
    # progressively turn on each trace for single slider   
    if i>0:
        count=plotnum[i-1]+count
    for j in range(plotnum[i]):
        step['args'][1][j+count] = True
        
    # add step to step list
    steps.append(step)
#setup slider and plot layouts
sliders = [dict(
                x=0,
                y=-0.05,
                currentvalue= {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'left'},
                steps = steps,
                ),]
fig.layout.sliders=sliders
fig.update_layout(
    autosize=False,
width=1000,
height=700,
margin=go.layout.Margin(
    l=50,
    r=50,
    b=100,
    t=100,
    pad=4
    ),
legend_orientation="h",
legend=dict(x=0, y=-0.35),
title = {
       'text': "Rank vs Number of Weeks on Billboard Top 100",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
xaxis_title = "Weeks",
yaxis_title = "Rank on Billboard Hot 100",
xaxis_tickformat = '',
 font=dict(
     family="Courier New, monospace",
     size=12,
     color="#7f7f7f"
 )
)
# set ranges for plots
fig.update_xaxes(range=[0, 70])
fig.update_yaxes(range=[0, 100])
fig.update_yaxes(autorange="reversed")
fig.show()

# plot onto browser
pio.renderers.default = 'browser'
pio.show(fig)
