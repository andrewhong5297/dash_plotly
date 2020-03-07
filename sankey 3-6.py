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

"""shaping uses dataset"""
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
# uses['hour'] = uses.index.hour
# uses['Day_of_week'] = uses.index.dayofweek

# BU2 = uses["Business Unit"] != "Total"
# uses = uses[BU2]
# BU3 = uses["Business Unit"] != "Net"
# uses = uses[BU3]

# """Changing Types and Standardizing"""
# uses['value'] = uses['value'].astype(float) #november 1st and 2nd 2019 have " -   " string instead of a 0 in them
# uses["value"]=uses["value"].div(1000000)

# BU =  uses["Business Unit"] != "Treasury"
# uses = uses[BU]#|BU2|BU3|BU4] #selecting BU to model

# df = uses
# fig = px.sunburst(uses, path=['Business Unit','Product'], values='value')

# credit to https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0
def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#4B8BBE','#306998','#FFE873','#FFD43B','#646464']
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

       # creating the sankey diagram
    data = dict(
        type='sankey',
        arrangement = "perpendicular", #perpendicular (move up down), freeform (movement affects others), snap (creates spaces in child)
        node = dict(
          pad = 15,
          thickness = 20,
          valuesuffix = "($m)",
          
          line = dict(
            color = "black",
            width = 0.5
          ),
          label = labelList,
          color = colorList
        ),

        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count']
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

cal_fig=px.density_heatmap(df2, x="sepal_width", y="sepal_length", marginal_x="rug", marginal_y="histogram")

"""can we make this an on-hover?"""
app.layout = html.Div([
    html.Div([
    dcc.Graph(id='sankey', figure={'layout': {'height':1500}}),
    ], style={'width': '58%', 'display': 'inline-block'}),
    
    html.Div([
    html.Label('Select Path for Sankey Chart'),
    dcc.Dropdown(
        id='Multi-Select Dropdown Path',
        options=[
        {'label': 'Borough', 'value': 'neighbourhood_group'},
        {'label': 'Neighbourhood', 'value': 'neighbourhood'},
        {'label': 'Rooms in Listing', 'value': 'room_type'},
        ], value=['neighbourhood_group','neighbourhood'],
        multi=True
        ),
    
    # html.Label('Select Business Area'),
    # dcc.Dropdown(
    #     id='Multi-Select Dropdown Business Area',
    #     options=[{'label': i, 'value': i} for i in available_indicators]
    #     , value=['Business Unit','Product'],
    #     multi=True
    #     ),
    # html.Label('Select Product'),
    # dcc.Dropdown(
    #     id='Multi-Select Dropdown Product',
    #     options=[{'label': i, 'value': i} for i in available_indicators]
    #     , value=['Business Unit','Product'],
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
    
    html.Label('Can we add a percent flow hover, as well as commentary box? also add color shading to sankey and research hovertools'),
    ], style={'width': '39%', 'float': 'right', 'display': 'inline-block'}),

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
    # [Input('month-slider', 'value'),
      # Input('day-slider', 'value'),
      [Input('Multi-Select Dropdown Path', 'value')])
      # Input('Multi-Select Dropdown Neighbourhood', 'value')])
def update_figure(value):#month,day,value):
    filtered_df=df
    # filtered_df = df[df.month == month]
    # filtered_df = filtered_df[filtered_df.date == day]
    # filtered_df=filtered_df[BU]
    a = value[0]
    if len(value)>1:
        b = value[1]
        if len(value)>2:
            c = value[2]
            if len(value)>3:
                d = value[3]
                return genSankey(filtered_df,cat_cols=[a,b,c,d],value_cols='number_of_reviews',title='Number of Reviews')
            return genSankey(filtered_df,cat_cols=[a,b,c],value_cols='number_of_reviews',title='Number of Reviews')
        return genSankey(filtered_df,cat_cols=[a,b],value_cols='number_of_reviews',title='Number of Reviews')
    return genSankey(filtered_df,cat_cols=[a],value_cols='number_of_reviews',title='Number of Reviews')

"""time series hover"""
# @app.callback(
#     Output('hover-line','figure'),
#     [Input('sankey','hoverData')])
# def update_hover(hoverData):
#     neighbourhood = hoverData['points'][0]["label"]
#     title="{} versus Price".format()
#     return create_time_series(dff, axis_type, title)

"""statistics dropdown"""
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