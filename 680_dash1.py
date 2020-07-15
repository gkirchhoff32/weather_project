### BME680 weather sensor project ###############
### Display real-time browser based data ########
### Dash code source: "PythonProgramming.net" ###
### BME680 code source: Adafruit ################
### Grant Kirchhoff, UC Berkeley ################
### 2020.06.01 ##################################

# NOTE: Hermosa IP 192.168.1.73
# Remember to use 192.168.x.xx:8050

# plotly modules
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import time
from collections import deque
import plotly.graph_objs as go
import random

# sensor modules
import board
import busio
import adafruit_bme680
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt
import numpy as np

from pandas import DataFrame

max_length = 50
times = deque(maxlen=max_length)
temp_vals = deque(maxlen=max_length)
gas_vals = deque(maxlen=max_length)
hum_vals = deque(maxlen=max_length)
pres_vals = deque(maxlen=max_length)
tot_time,tot_temp,tot_gas,tot_hum,tot_pres = [],[],[],[],[]

data_dict = {
                "Temperature":temp_vals,
                "Gas":gas_vals,
                "Humidity":hum_vals,
                "Pressure":pres_vals
             }

def update_obd_values(times, temp_vals, gas_vals, hum_vals, pres_vals):
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    
    times.append(time.time())     
    temp_vals.append(sensor.temperature)
    gas_vals.append(sensor.gas)
    hum_vals.append(sensor.humidity)
    pres_vals.append(sensor.pressure)

    tot_time.append(times[-1])
    tot_temp.append(temp_vals[-1])
    tot_gas.append(gas_vals[-1])
    tot_hum.append(hum_vals[-1])
    tot_pres.append(pres_vals[-1])

    return times, temp_vals, gas_vals, hum_vals, pres_vals
     
times, temp_vals, gas_vals, hum_vals, pres_vals = update_obd_values(times, temp_vals, gas_vals, hum_vals, pres_vals)     




# Dash
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]     
external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']     
app = dash.Dash('vehicle-data',     
                external_scripts=external_js,     
                external_stylesheets=external_css)

app.layout = html.Div([     
    html.Div([     
        html.H2('Weather Data',     
                style={'float': 'left',     
                       }),     
        ]),     
    dcc.Dropdown(id='weather-data-name',     
                 options=[{'label': s, 'value': s}     
                          for s in data_dict.keys()],     
                 value=['Temperature','Humidity','Pressure','Gas'],     
                 multi=True     
                 ),     
    html.Div(children=html.Div(id='graphs'), className='row'),     
    dcc.Interval(     
        id='graph-update',     
        interval=1000,     
        n_intervals=0),

##    html.Div(html.Div(['High Temperature:',html.H2(id='t1')])),

    dash_table.DataTable(id='data_table')
    
     
    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})     

# OLD METHOD FOR UPDATING MAX VALUE (CHECK BELOW FOR WRAPPER)
##@app.callback(     
##    [dash.dependencies.Output('graphs','children'),
##     dash.dependencies.Output('t1','children')],
##    [dash.dependencies.Input('weather-data-name', 'value'),     
##     dash.dependencies.Input('graph-update', 'n_intervals')],     
##    )
    
@app.callback(     
    [dash.dependencies.Output('graphs','children'),
     dash.dependencies.Output(component_id='data_table',component_property='data'),
     dash.dependencies.Output(component_id='data_table',component_property='columns')],
    [dash.dependencies.Input('weather-data-name', 'value'),     
     dash.dependencies.Input('graph-update', 'n_intervals')],     
    )     
def update_graph(data_names, n):     
    graphs = []     
    update_obd_values(times, temp_vals, gas_vals, hum_vals, pres_vals)
    
    if len(data_names)>2:     
        class_choice = 'col s12 m6 l4'     
    elif len(data_names) == 2:     
        class_choice = 'col s12 m6 l6'     
    else:     
        class_choice = 'col s12'     
     
    for data_name in data_names:
        if data_name=='Temperature':
            y_unit = 'C'
            fillcolor='#990000'
        elif data_name=='Humidity':
            y_unit = '%'
            fillcolor='#c6e2ff'
        elif data_name=='Pressure':
            y_unit = 'kPa'
            fillcolor='#ae624c'
        else:
            y_unit = 'Ohms'
            fillcolor='#cbcba9'
        data = go.Scatter(     
            x=list(times),     
            y=list(data_dict[data_name]),     
            name='Scatter',
            #mode='markers',
            marker_color='#000000',
            fill="tozeroy",     
            fillcolor=fillcolor
            )     
     
        graphs.append(html.Div(dcc.Graph(     
            id=data_name,     
            animate=True,     
            figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(times),max(times)]),     
                                                        yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),     
                                                        margin={'l':50,'r':1,'t':45,'b':1},     
                                                        title='{}'.format(data_name),
                                                        yaxis_title='{} ({})'.format(data_name,y_unit))}     
            ), className=class_choice))


##    RETURN FOR DISPLAYING OF max temperature
##    t1 = max(temp_vals)
##
##    return graphs,t1

    if len(tot_temp)>10:
        need_data = np.array([['%.2f'%(max(i)),'%.2f'%(min(i))] for i in [tot_temp[10:],tot_hum[10:],tot_pres[10:],tot_gas[10:]]])
        need_data = need_data.T.tolist()
        need_data[0].insert(0,'Max')
        need_data[1].insert(0,'Min')
    else:
        pass
    
    
        
    df = DataFrame(need_data,columns=['','Temperature (C)','Humidity (%)','Pressure (kPa)','Gas VOC (Ohms)'])
    columns = [{'name':col,'id':col} for col in df.columns]
    data = df.to_dict(orient='records')
                                 

    return graphs,data,columns
     
if __name__ == '__main__':     
    app.run_server(host='0.0.0.0', debug=False)






