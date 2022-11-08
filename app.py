# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 15:34:43 2022

@author: Angeliki.Loukatou
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input


file = "GSPs_DCs.xlsx"
df = pd.read_excel(file, sheet_name='GSPs')
coordinates = pd.read_excel(file, sheet_name='Lat_Lon')
dict_df = df.set_index('Name').T.to_dict('list')

df_fes_orig = pd.read_excel("Data-workbook2022_V004.xlsx", sheet_name='BB1')
df_fes_orig['GSPs'] = df_fes_orig['GSP'].map(dict_df)
df_fes_orig = df_fes_orig.applymap(lambda x: x if not isinstance(x, list) else x[0] if len(x) else '')


app = dash.Dash(__name__)


app.layout=html.Div([
    html.H1("Battery storage deployment in 2050"),
    html.P("Choose Future Energy Scenario"),

    dcc.Dropdown(id='graph-choice-1',
                 options=[{'label':'Leading the Way', 'value':'Leading the Way'},
                          {'label':'Consumer Transformation', 'value':'Consumer Transformation'},
                          {'label':'System Transformation', 'value':'System Transformation'},
                          {'label':'Falling Short', 'value':'Falling Short'}],
                          
                 value='select scenario'
                 ),
    html.P("Choose Future Year"),
    dcc.Dropdown(id='graph-choice-2',
                 options=[{'label':2030, 'value':2030},
                          {'label':2040, 'value':2040},
                          {'label':2050, 'value':2050}],
                 
                 value='select year'),
    dcc.Graph(id='my-graph', figure={}
              )
])


@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    [Input(component_id='graph-choice-1', component_property='value'),
     Input(component_id='graph-choice-2', component_property='value')]
)

def interactive_graphs(selected_scenario, selected_year):
    
    df_fes = df_fes_orig[df_fes_orig['Building Block ID Number'] == 'Srg_BB001']
    df_fes = df_fes[df_fes['FES Scenario'] == str(selected_scenario)]
    
    sorted_coordinates = pd.DataFrame(columns=['lat','lon'])
    for i in range(len(df_fes)):
        GSP = df_fes.reset_index().loc[i,'GSPs']
        df_temp = coordinates[coordinates['GSP ID']==GSP]
        try:
            sorted_coordinates.loc[i,'lat'] = df_temp.reset_index().loc[0,'Latitude']
            sorted_coordinates.loc[i,'lon'] = df_temp.reset_index().loc[0,'Longitude']
        except:
            sorted_coordinates.loc[i,'lat'] = np.nan
            sorted_coordinates.loc[i,'lon'] = np.nan


    df = pd.DataFrame(columns = ['latitude', 'longitude', 'Capacity'])
    df.loc[:,'latitude'] = sorted_coordinates['lat']
    df.loc[:,'longitude'] = sorted_coordinates['lon']
    df.loc[:,'Capacity'] = df_fes[selected_year].reset_index()[selected_year]
    df = df[df['Capacity']<600]
    
    return px.scatter_mapbox(df, lat='latitude', lon='longitude',color='Capacity',size='Capacity',hover_data=['Capacity'],
                        center=dict(lat=51.5, lon=-3.17), zoom=2.5,color_continuous_scale=px.colors.cyclical.Twilight,
                        mapbox_style="stamen-terrain",width=900, height=600)
           


if __name__=='__main__':
    app.run_server(debug=False)