import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)





app = Dash(__name__)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                    {"label": "1.Agriculture, forestry, fishing, food, beverages, tobacco ", 
                    "value": "1.Agriculture, forestry, fishing, food, beverages, tobacco "},
                    {"label":"2.Mining, quarrying, refinery, fuels, chemicals, electricity, water, waste treatment ", 
                    "value": "2.Mining, quarrying, refinery, fuels, chemicals, electricity, water, waste treatment "},
                    {"label":"3.Construction, wood, glass, stone, basic metals, housing, electrical appliances, furniture  ",
                     "value": "3.Construction, wood, glass, stone, basic metals, housing, electrical appliances, furniture  "},
                    {"label":"4.Textile, apparel, shoes ", 
                    "value": "4.Textile, apparel, shoes "},
                    {"label":"5.Transport equipment and services, travel, postal services", 
                    "value": "5.Transport equipment and services, travel, postal services"},
                    {"label":"6.ICT, media, computers, business and financial services", 
                    "value": "6.ICT, media, computers, business and financial services"},
                    {"label":"7.Health, pharmaceuticals, education, cultural, sport", 
                    "value": "7.Health, pharmaceuticals, education, cultural, sport"},
                    {"label":"8.Government, military and other", 
                    "value": "8.Government, military and other"}],
                 multi=False,
                 value="1.Agriculture, forestry, fishing, food, beverages, tobacco ",
                 style={'width': "60%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])


# ------------------------------------------------------------------------------


import_df = pd.read_csv('import_df.csv')

import_df = import_df.fillna(0)
import_tot = import_df[import_df['Code'] == 'TOTAL']
import_tot = import_tot[import_tot.columns.difference(['Code','Product label', 'BEC'])]
import_tot_country = list(import_tot['Country'])


import_tot_milion = import_tot[import_tot.columns.difference(['Country'])]/1000000
import_tot_milion_1 = import_tot_milion.round(0)

import_tot_milion_1 = import_tot_milion_1.reset_index(drop=True)


import numpy as np
import_tot_dict = {}
for k, v in zip(import_tot_country, range(len(import_tot_milion_1))):
    import_tot_dict[k] = {}
    import_tot_dict[k]['values'] = import_tot_milion_1.iloc[v]
    val_list_1 = list(import_tot_milion_1.iloc[v])
    val_list_1.insert(0, val_list_1[0])
    minus = np.array(val_list_1[1:]) - np.array(val_list_1[:-1])
    minus_add = []
    v1 = 0
    for v in minus:
        if len(minus_add) == 0:
            minus_add.append(0)
        else:
            minus_add.append(v+v1)
        v1 = v

    import_tot_dict[k]['minus'] = minus_add
    
year = [k.split(' ')[3] for k in import_tot_dict['Australia']['values'].keys()]
country = [k for k in import_tot_dict.keys()]


#############
import_df_999999 = import_df[import_df['Code']=='999999']
import_df_val = import_df.drop(import_tot.index)
import_df_val = import_df_val.drop(import_df_999999.index)

import_country_val_dict = {}
for con in country:
    import_country_val_dict[con] = {}
    import_country_val_dict[con]['df'] = import_df_val[import_df_val['Country'] == con]
    import_country_val_dict[con]['BEC'] = import_country_val_dict[con]['df'].groupby('BEC').sum()/100000
    import_country_val_dict[con]['BEC'] = import_country_val_dict[con]['BEC'].round(0)
    import_country_val_dict[con]['BEC'] = import_country_val_dict[con]['BEC'].reset_index()
    import_country_val_dict[con]['BEC'].columns = ['BEC']+year
    
    
BEC_Import_Dict = {}
for con in country:
    for i in range(0,8):
        A = list(import_country_val_dict[con]['BEC'].iloc[i])
        if A[0] not in BEC_Import_Dict.keys():
            BEC_Import_Dict[A[0]] = {}    
        BEC_Import_Dict[A[0]][con] = np.array(A[1:])
        
        
        
list_1 = list(BEC_Import_Dict.keys())
df_ = pd.DataFrame()


for i in list_1:
    a1 = pd.DataFrame(BEC_Import_Dict[i])
    a1['bec'] = i
    a1['year'] = year
    df_ = pd.concat([a1, df_])
    
    
    
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    #dff = df.copy()
    #dff = dff[dff["Year"] == option_slctd]
    #dff = dff[dff["Affected by"] == "Varroa_mites"]

    dff_ = df_.copy()
    dff_ = dff_[dff_["bec"] == option_slctd]
    dff_ = dff_[dff_.columns.difference(['bec'])]
    dff_ = dff_.set_index('year')
    fig = px.line(dff_, markers=True)

    #for i in range(len(fig.data)):
    #    fig.data[i]['mode']= 'markers+lines'

    return container, fig
    
    
if __name__ == '__main__':
    app.run_server(port = 8050, dev_tools_ui=True, #debug=True,
              dev_tools_hot_reload =True, threaded=True)
