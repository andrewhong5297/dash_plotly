# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 10:09:03 2020
@author: honandre
"""
import pandas as pd
from pandas import melt

import seaborn as sns
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

# credit to https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0
def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
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
          # color = color
        )
      )
    
    layout =  dict(
        title = title,
        font = dict(
          size = 15
        )
    )
    
    fig = dict(data=[data], layout=layout)
    return fig

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
            dcc.Graph(id='sankey', style={'layout': {'height':1000}}),
    
    ],style={'width': '58%', 'display': 'inline-block'}), #left side div
    
    html.Div([
        html.Table([
            html.Tr([html.Td(['Histogram of:']), html.Td(id='hover')])
        ]), 
            dcc.Graph(id='hover-line'),
        
        html.Label('Limits Calendar Heatmap, to add limit choice'),
            dcc.Graph(id='calendar', figure=cal_fig),
        
        html.Label('Can we add a percent flow hover, as well as commentary box? also add color shading to sankey and research hovertools'),
    
    ], style={'width': '39%', 'float': 'right', 'overflowY': 'scroll', 'display': 'inline-block'}), #right side div

])#, style={'columnCount': 2}) #overall style)

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
# add multiple inputs, for path as well
@app.callback(
    Output('sankey', 'figure'),
      [Input('Multi-Select Dropdown Path', 'value'),
       Input('Multi-Select Dropdown Business Area', 'value')])
def update_figure(path,select):#month,day,value):
    if len(select)!=0:
        filtered_df=df[df["neighbourhood"]==select[0]]
        if len(select)==2:
            filtered_df=df[(df["neighbourhood"]==select[0]) | (df["neighbourhood"]==select[1])]
    else:
        filtered_df=df
    a = path[0]
    if len(path)>1:
        b = path[1]
        if len(path)>2:
            c = path[2]
            if len(path)>3:
                d = path[3]
                return genSankey(filtered_df,cat_cols=[a,b,c,d],value_cols='number_of_reviews',title='Number of Reviews')
            return genSankey(filtered_df,cat_cols=[a,b,c],value_cols='number_of_reviews',title='Number of Reviews')
        return genSankey(filtered_df,cat_cols=[a,b],value_cols='number_of_reviews',title='Number of Reviews')
    return genSankey(filtered_df,cat_cols=[a],value_cols='number_of_reviews',title='Number of Reviews')

if __name__ == '__main__':
    app.run_server(debug=False)