# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 10:09:03 2020
@author: Andrew Hong
"""
import pandas as pd
from pandas import melt

"""shaping Uses of Funding dataset"""
# uses = pd.read_excel(r'F:\Python Scripts\liquidity-risk-project\BCI_S&U_Trend.xlsx', sheet_name=0)

# uses = melt(uses, id_vars=["Date"],var_name="Business Unit")
# new = uses["Business Unit"].str.split(", ", n=None, expand = True)
# uses["Business Unit"]=new[0]
# uses["Product"]=new[1]
# uses = uses[['Date','Business Unit','Product','value']]
# uses['Date'] = pd.to_datetime(uses['Date'])
# # start_date = "2019-1-30"
# # end_date = "2020-1-31"
# # date_range = uses["Date"]== start_date #) & (uses["Date"] <= end_date) # time filter
# # uses = uses[date_range]
# uses['Date2']=uses['Date']

# uses.set_index('Date', inplace=True)
# uses['year'] = uses.index.year
# uses['month'] = uses.index.month
# uses['date'] = uses.index.day
# uses['Day_of_week'] = uses.index.dayofweek

# """Changing Types and Standardizing"""
# uses['value'] = uses['value'].astype(float) #november 1st and 2nd 2019 have " -   " string instead of a 0 in them
# uses["value"]=uses["value"].div(1000000)

# df = uses #setting this so I don't have to change variable names in dashboard if I change datasets. 

"""for getSankey test purposes"""
# df = pd.read_csv(r'C:\Users\Andrew\Documents\Python Scripts\data set\AB_NYC_2019.csv')
# cat_cols = ["neighbourhood","room_type"]
# value_cols="number_of_reviews"
# title="AirBnb Review Sankey"

# modified function from https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0
def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram',hover=""):
    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#F27420','#4994CE','#FABC13','#7FC241','#D3D3D3']

    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp

    # remove duplicates from labelList
    labelList = list(dict.fromkeys(labelList))
                   
    # define colors based on number of levels
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum  
       
    # transform df into a source-target pair
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            sourceTargetDf.columns = ['source','target','count']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            tempDf.columns = ['source','target','count']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()
    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))
    
    #setting hover node links to source color
    colorLink = ["#D3D3D3"]*len(sourceTargetDf['sourceID']) #default color
    if len(hover)!=0:
        try:
            linkcolor = colorList[labelList.index(hover)]
            b = sourceTargetDf[sourceTargetDf['source']==hover]
            b = b.index
            for i in b:
                colorLink[i]=linkcolor
        except ValueError:
            print("WARNING:", hover, "not found in source")
        
    #auto size graphic based on number of nodes with a minimum of 1000
    heightY = max(colorNumList)*15
    if heightY <=1000:
        heightY= str(1000)
    else:
        heightY = str(heightY)
        
    # creating the sankey diagram
    data = dict(
        type='sankey',
        arrangement = "perpendicular", #perpendicular (move up down), freeform (movement affects others), snap (creates spaces in child)
        node = dict(
          pad = 20,
          thickness = 20,
          valuesuffix = "($m)",
          
          line = dict(
            color = "black",
            width = 0
          ),
          label = labelList,
          color = colorList
        ),
    
        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count'],
          color = colorLink 
        )
      )
    
    layout =  dict(
        title = title,
        font = dict(
          size = 15
        ),
        height = heightY
    )
    
    fig = dict(data=[data], layout=layout)
    return fig


def create_time_series(dff,label, title):
    return {
        'data': [dict(
            x=dff['neighbourhood'],
            y=dff['number_of_reviews'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear'}, #if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }

# """put into dash later, with dropdown for limit and date input tie in to slider"""
from plotly.offline import plot
import plotly.express as px
df2 = px.data.iris()

""" dash"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(r'C:\Users\Andrew\Documents\Python Scripts\data set\AB_NYC_2019.csv')
available_indicators = df['neighbourhood'].unique()

cal_fig=px.density_heatmap(df2, x="sepal_width", y="sepal_length")# marginal_x="rug", marginal_y="histogram")

""" adding what if analysis as tab two? dragging of forecast points or something. also seasonal_decomp then plot with plotly"""

app.layout = html.Div([
    html.Div([
        
    html.Label('Select Path for Breakdown'),
    dcc.Dropdown(
        id='Multi-Select Dropdown Path',
        options=[
        {'label': 'Borough', 'value': 'neighbourhood_group'},
        {'label': 'Neighbourhood', 'value': 'neighbourhood'},
        {'label': 'Rooms in Listing', 'value': 'room_type'},
        ], value=['neighbourhood_group','room_type'],
        multi=True
        ),
    
    html.Label('Select Business Area'),
    dcc.Dropdown(
        id='Multi-Select Dropdown Business Area',
        options=[{'label': i, 'value': i} for i in available_indicators]
        , value=[],
        multi=True
        ),
    dcc.Graph(id='sankey'),#, style={'layout': {'height':1000}}),
    ],style={'width': '58%', 'display': 'inline-block'}), #left side div
    
    html.Div([
    # html.Label('Select Product'), #make for entity and counterparty too
    # dcc.Dropdown(
    #     id='Multi-Select Dropdown Product',
    #     options=[{'label': i, 'value': i} for i in available_indicators]
    #     , value=[],
    #     multi=True
    #     ),
    
    # dcc.Slider(
    #     id='month-slider',
    #     min=df['month'].min(),
    #     max=df['month'].max(),
    #     value=df['month'].min(),
    #     marks={str(date): str(date) for date in df['month'].unique()},
    #     step=None
    # ),

    # dcc.Slider(
    #     id='day-slider',
    #     min=df['date'].min(),
    #     max=df['date'].max(),
    #     value=df['date'].min(),
    #     marks={str(date): str(date) for date in df['date'].unique()},
    #     step=None
    # ),

    # dcc.Dropdown(
    #             id='business-for-des',
    #             options=[{'label': i, 'value': i} for i in available_indicators],
    #             value='Fixed Income Financing'
            # ),
    # html.Table([
    #     html.Tr([html.Td(['Mean']), html.Td(id='Mean')]),
    #     html.Tr([html.Td(['Standard Deviation']), html.Td(id='Standard Deviation')]),
    #     html.Tr([html.Td(['Min']), html.Td(id='Min')]),
    #     html.Tr([html.Td(['First Quartile']), html.Td(id='First Quartile')]),
    #     html.Tr([html.Td(['Second Quartile/Median']), html.Td(id='Second Quartile/Median')]),
    #     html.Tr([html.Td(['Third Quartile']), html.Td(id='Third Quartile')]),
    #     html.Tr([html.Td(['Max']), html.Td(id='Max')]),
    # ]), 
    html.Table([
        html.Tr([html.Td(['Histogram of:']), html.Td(id='hover')])
    ]), 
    dcc.Graph(id='hover-line'),
    
    html.Label('Limits Calendar Heatmap, to add limit choice'),
    dcc.Graph(id='calendar', figure=cal_fig),
    
    html.Label('Can we add a percent flow hover, as well as commentary box? second tab to focus on maximum change detection as default for dumbell plot dropdown, this should be discussed before implement'),
    html.Label('Also to change date selection to just year, and make month/day selection from calendar heatmap. Limit dropdown by enity, and by scenario'),
    ], style={'width': '39%', 'float': 'right', 'overflowY': 'scroll', 'display': 'inline-block'}), #right side div

])#, style={'columnCount': 2}) #overall style

"""hover histogram"""
import json
@app.callback(
    Output('hover','children'),
    [Input('sankey','hoverData')])
def show_click(hoverData):
    a=hoverData['points'][0]["label"]
    return a

@app.callback(
    Output('hover-line','figure'),
    [Input('sankey','hoverData')])
def show_click_line(hoverData):
    a = hoverData['points'][0]["label"]
    dftemp=df[df["neighbourhood"]==a]
    if dftemp.empty:
        dftemp=df[df["neighbourhood_group"]==a]
        if dftemp.empty:
            dftemp=df[df["room_type"]==a]
    return px.histogram(dftemp, x="number_of_reviews")

"""sankey graph"""
@app.callback(
    Output('sankey', 'figure'),
    # [Input('month-slider', 'value'),
      # Input('day-slider', 'value'),
      [Input('Multi-Select Dropdown Path', 'value'),
       Input('Multi-Select Dropdown Business Area', 'value'),
       Input('sankey','hoverData')])
def update_figure(path,select,hov):#month,day): 
    if len(select)!=0:
        filtered_df=df[df["neighbourhood"].isin(select)]
    else:
        filtered_df=df
    
    # #should be same type of loop as above... I wonder if it's easier to create a function? 
    # filtered_df=filtered_df[product]
    # filtered_df=filtered_df[entity]
    # filtered_df=filtered_df[counterparty]
    # filtered_df=filtered_df[currency] #this one will be a challenge

    # # replace with calendar click later
    # filtered_df = df[df.month == month]
    # filtered_df = filtered_df[filtered_df.date == day]
        
    #part of setting link color
    try: 
        hov = hov['points'][0]["label"]
    except TypeError:
        hov=""

    return genSankey(filtered_df,cat_cols=path,value_cols='number_of_reviews',title='Number of Reviews',hover = hov)

"""time series hover to replace current histogram"""
# @app.callback(
#     Output('hover-line','figure'),
#     [Input('sankey','hoverData')])
# def update_hover(hoverData):
#     neighbourhood = hoverData['points'][0]["label"]
#     title="{} versus Price".format()
#     return create_time_series(dff, axis_type, title)

"""statistics dropdown, maybe unnescessary see wind dashboard for distribution graph?"""
# @app.callback(
#     [Output('Mean', 'children'),
#      Output('Standard Deviation', 'children'),
#      Output('Min', 'children'),
#      Output('First Quartile', 'children'),
#      Output('Second Quartile/Median', 'children'),
#      Output('Third Quartile', 'children'),
#      Output('Max', 'children')],
#     [Input('business-for-des', 'value')])
# def describe_output(value):
#     filtered_df = df[df['Business Unit']==value]
#     pivot = filtered_df.pivot_table(index=filtered_df.index,columns="Business Unit",values="value",aggfunc="sum")
#     des = pivot.describe().round(2)
#     return des.iat[1,0],des.iat[2,0],des.iat[3,0],des.iat[4,0],des.iat[5,0],des.iat[6,0],des.iat[7,0]
 
if __name__ == '__main__':
    app.run_server(debug=False)