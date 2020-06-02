### BME680 weather sensor project ###############
### Display real-time browser based data ########
### Dash code source: "PythonProgramming.net" ###
### BME680 code source: Adafruit ################
### Grant Kirchhoff, UC Berkeley ################
### 2020.06.01 ##################################

# plotly modules
import dash
import dash_core_components as dcc
import dash_html_components as html
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
    if len(times) == 1:     
        #starting relevant values
        
        for i in [temp_vals,gas_vals,hum_vals,pres_vals]:
            i.append(1)
        
    else:
        temp_vals.append(sensor.temperature)
        gas_vals.append(sensor.gas)
        hum_vals.append(sensor.humidity)
        pres_vals.append(sensor.pressure)

    return times, temp_vals, gas_vals, hum_vals, pres_vals
     
times, temp_vals, gas_vals, hum_vals, pres_vals = update_obd_values(times, temp_vals, gas_vals, hum_vals, pres_vals)     
tot_time.append(times[-1])
tot_temp.append(temp_vals[-1])
tot_gas.append(gas_vals[-1])
tot_hum.append(hum_vals[-1])
tot_pres.append(pres_vals[-1])




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
     
    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})     
     
@app.callback(     
    dash.dependencies.Output('graphs','children'),     
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
        data = go.Scatter(     
            x=list(times),     
            y=list(data_dict[data_name]),     
            name='Scatter',     
            fill="tozeroy",     
            fillcolor="#6897bb"     
            )     
     
        graphs.append(html.Div(dcc.Graph(     
            id=data_name,     
            animate=True,     
            figure={'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(times),max(times)]),     
                                                        yaxis=dict(range=[min(data_dict[data_name]),max(data_dict[data_name])]),     
                                                        margin={'l':50,'r':1,'t':45,'b':1},     
                                                        title='{}'.format(data_name))}     
            ), className=class_choice))     
     
    return graphs     
     
if __name__ == '__main__':     
    app.run_server(host='0.0.0.0', debug=False)





